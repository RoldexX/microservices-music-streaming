# app/models/user.py
from uuid import UUID
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, ConfigDict


class UserRole(str, Enum):
    USER = "user"
    ARTIST = "artist"
    ADMIN = "admin"


class UserBase(BaseModel):
    email: EmailStr
    phone: str | None = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    is_blocked: bool
    has_2fa: bool
    role: UserRole
    created_at: datetime
    updated_at: datetime
