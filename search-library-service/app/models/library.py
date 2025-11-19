# app/models/library.py
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class PlaylistBase(BaseModel):
    title: str
    is_public: bool = False


class PlaylistCreate(PlaylistBase):
    pass


class PlaylistRead(PlaylistBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID


class PlaylistTrackCreate(BaseModel):
    track_id: UUID
    position: int | None = None


class FavoriteTrackCreate(BaseModel):
    track_id: UUID


class FavoriteTrackRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    track_id: UUID
