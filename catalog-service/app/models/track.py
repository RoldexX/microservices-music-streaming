# app/models/track.py
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class TrackBase(BaseModel):
    title: str
    duration_sec: int
    file_path: str | None = None  # путь/ключ к файлу, но без реальной интеграции
    is_published: bool = False


class TrackCreate(BaseModel):
    title: str
    duration_sec: int = Field(..., ge=0, description="Duration must be >= 0")
    file_path: str | None = None


class TrackUpdate(BaseModel):
    title: str | None = None
    duration_sec: int | None = None
    file_path: str | None = None


class TrackRead(TrackBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    album_id: UUID
