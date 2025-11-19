# app/models/profile.py
from uuid import UUID
from pydantic import BaseModel, AnyHttpUrl, ConfigDict


class ProfileBase(BaseModel):
    display_name: str
    region: str
    avatar_url: AnyHttpUrl | None = None
    is_closed: bool = False


class ProfileCreate(BaseModel):
    user_id: UUID
    display_name: str
    region: str


class ProfileUpdate(BaseModel):
    display_name: str | None = None
    region: str | None = None
    avatar_url: AnyHttpUrl | None = None
    is_closed: bool | None = None


class ProfileRead(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
