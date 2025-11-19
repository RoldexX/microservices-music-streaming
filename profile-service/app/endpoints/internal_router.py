# app/endpoints/internal_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.profile import ProfileCreate, ProfileRead
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/internal", tags=["Internal"])


def service(db: Session = Depends(get_db)) -> ProfileService:
    return ProfileService(db)


@router.post("/profiles", response_model=ProfileRead)
def internal_create_profile(
    data: ProfileCreate,
    svc: ProfileService = Depends(service),
):
    try:
        return svc.create_profile(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
