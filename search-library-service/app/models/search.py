# app/models/search.py
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class SearchItemType(str):
    TRACK = "track"
    ALBUM = "album"


class SearchItemBase(BaseModel):
    object_type: str  # 'track' или 'album'
    object_id: UUID
    title: str
    artist_name: str | None = None


class SearchItemRead(SearchItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class SearchResponse(BaseModel):
    query: str
    type: str  # 'track', 'album', 'all'
    items: list[SearchItemRead]
