# app/models/notification.py
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotificationBase(BaseModel):
    title: str
    body: str
    is_read: bool = False


class NotificationCreate(BaseModel):
    user_id: UUID
    title: str
    body: str


class NotificationRead(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime


class NotificationSettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    enabled: bool
    new_releases: bool
    recommendations: bool
    system: bool


class NotificationSettingsUpdate(BaseModel):
    enabled: bool | None = None
    new_releases: bool | None = None
    recommendations: bool | None = None
    system: bool | None = None


class MarkReadRequest(BaseModel):
    notification_ids: list[UUID] | None = None  # если None — пометить все
