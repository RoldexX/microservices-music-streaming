# app/endpoints/auth_router.py
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import UserCreate, UserRead
from app.models.auth import (
    LoginRequest,
    TokenPair,
    TokenRefreshRequest,
    TwoFAChangeRequest,
    RegisterResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db=db)


@router.post("/register", response_model=RegisterResponse)
def register(
    data: UserCreate,
    service: AuthService = Depends(get_auth_service),
):
    try:
        user = service.register(data)
        return RegisterResponse(user_id=user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenPair)
def login(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return service.login(data.email, data.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/token/refresh", response_model=TokenPair)
def refresh_token(
    data: TokenRefreshRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return service.refresh_tokens(data.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{user_id}/2fa", response_model=UserRead)
def change_2fa(
    user_id: UUID,
    body: TwoFAChangeRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return service.set_2fa(user_id=user_id, enabled=body.enabled)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
