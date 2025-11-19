# app/endpoints/profile_router.py
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.profile import ProfileRead, ProfileUpdate
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profiles", tags=["Profile"])


def service(db: Session = Depends(get_db)) -> ProfileService:
    return ProfileService(db)


@router.get("/me", response_model=ProfileRead)
def get_my_profile(user_id: UUID, svc: ProfileService = Depends(service)):
    # В учебной работе user_id передается параметром
    try:
        return svc.get_profile(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/me", response_model=ProfileRead)
def update_my_profile(
    user_id: UUID,
    data: ProfileUpdate,
    svc: ProfileService = Depends(service),
):
    try:
        return svc.update_profile(user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
