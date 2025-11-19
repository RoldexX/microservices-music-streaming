# app/services/auth_service.py
import hashlib
from datetime import datetime, timedelta
from typing import Tuple
from uuid import UUID

import jwt
from sqlalchemy.orm import Session

from app.models.user import UserCreate, UserRead
from app.models.auth import TokenPair
from app.repositories.user_repository import UserRepository
from app.services.messaging import MessagingService
from app.services.profile_client import ProfileClient
from app.settings import settings
from app.schemas.user import User as UserORM


class AuthService:
    def __init__(
        self,
        db: Session,
        messaging: MessagingService | None = None,
        profile_client: ProfileClient | None = None,
    ) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.messaging = messaging or MessagingService()
        self.profile_client = profile_client or ProfileClient()

    # ---------------- PASSWORD HASHING ---------------- #

    @staticmethod
    def _hash_password(password: str) -> str:
        # Для учебных целей — простой SHA256. В реальных системах использовать bcrypt/argon2.
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        return hashlib.sha256(password.encode("utf-8")).hexdigest() == password_hash

    # ---------------- JWT TOKEN UTILS ---------------- #

    def _create_access_token(self, user: UserORM) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expires_minutes)
        payload = {
            "sub": str(user.id),
            "type": "access",
            "exp": expire,
        }
        return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)

    def _create_refresh_token(self, user: UserORM) -> str:
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expires_days)
        payload = {
            "sub": str(user.id),
            "type": "refresh",
            "exp": expire,
        }
        return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)

    def _decode_token(self, token: str) -> dict:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])

    # ---------------- CORE OPERATIONS ---------------- #

    def register(self, data: UserCreate) -> UserRead:
        existing = self.user_repo.get_by_email(data.email)
        if existing:
            raise ValueError("User with this email already exists")

        password_hash = self._hash_password(data.password)
        user_read = self.user_repo.create_user(data, password_hash)

        # Синхронный HTTP-вызов в profile-service
        self.profile_client.create_profile_for_new_user(
            user_id=str(user_read.id),
            email=user_read.email,
        )

        # Публикуем событие в RabbitMQ
        self.messaging.publish_user_registered(
            user_id=str(user_read.id),
            email=user_read.email,
        )

        return user_read

    def login(self, email: str, password: str) -> TokenPair:
        user_orm = self.user_repo.get_by_email(email)
        if not user_orm:
            raise ValueError("Invalid credentials")

        if not self._verify_password(password, user_orm.password_hash):
            raise ValueError("Invalid credentials")

        if not user_orm.is_active or user_orm.is_blocked:
            raise ValueError("User is blocked or inactive")

        access_token = self._create_access_token(user_orm)
        refresh_token = self._create_refresh_token(user_orm)

        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    def refresh_tokens(self, refresh_token: str) -> TokenPair:
        try:
            payload = self._decode_token(refresh_token)
        except jwt.PyJWTError:
            raise ValueError("Invalid refresh token")

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token payload")

        user_orm = self.user_repo.get_by_id(user_id)
        if not user_orm:
            raise ValueError("User not found")

        access_token = self._create_access_token(user_orm)
        new_refresh_token = self._create_refresh_token(user_orm)

        return TokenPair(access_token=access_token, refresh_token=new_refresh_token)

    def set_2fa(self, user_id: UUID | str, enabled: bool) -> UserRead:
        return self.user_repo.set_2fa(user_id, enabled)
