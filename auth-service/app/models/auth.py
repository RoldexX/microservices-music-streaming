# app/models/auth.py
from uuid import UUID
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_id: str | None = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TwoFAChangeRequest(BaseModel):
    enabled: bool


class RegisterResponse(BaseModel):
    user_id: UUID
