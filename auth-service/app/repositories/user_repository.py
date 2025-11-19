# app/repositories/user_repository.py
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.schemas.user import User as UserORM
from app.models.user import UserCreate, UserRead, UserRole


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_email(self, email: str) -> Optional[UserORM]:
        return self.db.query(UserORM).filter(UserORM.email == email).first()

    def get_by_id(self, user_id: UUID | str) -> Optional[UserORM]:
        return self.db.query(UserORM).filter(UserORM.id == str(user_id)).first()

    def create_user(self, data: UserCreate, password_hash: str) -> UserRead:
        user = UserORM(
            email=data.email,
            phone=data.phone,
            password_hash=password_hash,
            is_active=True,
            is_blocked=False,
            has_2fa=False,
            role=UserRole.USER,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return UserRead.model_validate(user)

    def set_2fa(self, user_id: UUID | str, enabled: bool) -> UserRead:
        user = self.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        user.has_2fa = enabled
        self.db.commit()
        self.db.refresh(user)
        return UserRead.model_validate(user)
