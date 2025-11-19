# app/schemas/user.py
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, DateTime, Enum as SAEnum

from app.database import Base
from app.models.user import UserRole


class User(Base):
    __tablename__ = "users"

    # Для SQLite используем строковый UUID
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)
    has_2fa = Column(Boolean, default=False, nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.USER, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
