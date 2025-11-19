# app/models/playback.py
from uuid import UUID
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class PlaybackStatus(str, Enum):
    PLAYING = "playing"
    PAUSED = "paused"
    FINISHED = "finished"
    STOPPED = "stopped"


class PlaybackStartRequest(BaseModel):
    user_id: UUID
    track_id: UUID
    context_type: str | None = None  # 'album', 'playlist', 'radio'
    context_id: UUID | None = None
    volume: int = 50  # 0–100


class PlaybackSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    track_id: UUID
    status: PlaybackStatus
    position_sec: int
    volume: int
    context_type: str | None = None
    context_id: UUID | None = None
    started_at: datetime
    updated_at: datetime


class SetVolumeRequest(BaseModel):
    volume: int  # 0–100


class SimpleResponse(BaseModel):
    status: str
