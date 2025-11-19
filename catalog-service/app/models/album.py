# app/models/album.py
from uuid import UUID
from datetime import date

from pydantic import BaseModel, AnyHttpUrl, ConfigDict


class AlbumBase(BaseModel):
    title: str
    artist_name: str
    release_date: date | None = None
    cover_url: AnyHttpUrl | None = None
    is_published: bool = False


class AlbumCreate(BaseModel):
    title: str
    artist_name: str
    release_date: date | None = None
    cover_url: AnyHttpUrl | None = None


class AlbumUpdate(BaseModel):
    title: str | None = None
    artist_name: str | None = None
    release_date: date | None = None
    cover_url: AnyHttpUrl | None = None


class AlbumRead(AlbumBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
