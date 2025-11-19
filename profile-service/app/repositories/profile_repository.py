# app/repositories/profile_repository.py
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.schemas.profile import Profile as ProfileORM
from app.models.profile import ProfileCreate, ProfileUpdate, ProfileRead


class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: str | UUID) -> Optional[ProfileORM]:
        return self.db.query(ProfileORM).filter(ProfileORM.user_id == str(user_id)).first()

    def create(self, data: ProfileCreate) -> ProfileRead:
        profile = ProfileORM(
            user_id=str(data.user_id),
            display_name=data.display_name,
            region=data.region,
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return ProfileRead.model_validate(profile)

    def update(self, user_id: UUID | str, data: ProfileUpdate) -> ProfileRead:
        profile = self.get_by_user_id(user_id)
        if not profile:
            raise ValueError("Profile not found")

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, key, value)

        self.db.commit()
        self.db.refresh(profile)

        return ProfileRead.model_validate(profile)
