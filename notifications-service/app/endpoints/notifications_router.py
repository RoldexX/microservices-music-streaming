# app/endpoints/notifications_router.py
from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.notification import (
    NotificationRead,
    NotificationSettingsRead,
    NotificationSettingsUpdate,
    MarkReadRequest,
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/me/notifications", tags=["Notifications"])


def service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(db)


@router.get("/", response_model=List[NotificationRead])
def get_notifications(
    user_id: UUID,
    include_read: bool = Query(True),
    svc: NotificationService = Depends(service),
):
    return svc.list_notifications(user_id, include_read)


@router.post("/mark-read")
def mark_read(
    user_id: UUID,
    body: MarkReadRequest,
    svc: NotificationService = Depends(service),
):
    svc.mark_read(user_id, body.notification_ids)
    return {"status": "ok"}


@router.get("/settings", response_model=NotificationSettingsRead)
def get_settings(
    user_id: UUID,
    svc: NotificationService = Depends(service),
):
    return svc.get_settings(user_id)


@router.put("/settings", response_model=NotificationSettingsRead)
def update_settings(
    user_id: UUID,
    data: NotificationSettingsUpdate,
    svc: NotificationService = Depends(service),
):
    if not data.model_dump(exclude_unset=True):
        raise HTTPException(status_code=400, detail="No fields to update")
    return svc.update_settings(user_id, data)
