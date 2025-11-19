# app/services/profile_service.py
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.profile import ProfileCreate, ProfileUpdate, ProfileRead
from app.repositories.profile_repository import ProfileRepository
from app.services.messaging import MessagingService


class ProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProfileRepository(db)
        self.messaging = MessagingService()

    def create_profile(self, data: ProfileCreate) -> ProfileRead:
        profile = self.repo.create(data)

        # Публикуем событие
        self.messaging.profile_created(str(data.user_id))

        return profile

    def get_profile(self, user_id: UUID | str) -> ProfileRead:
        profile = self.repo.get_by_user_id(user_id)
        if not profile:
            raise ValueError("Profile not found")
        return ProfileRead.model_validate(profile)

    def update_profile(self, user_id: UUID | str, data: ProfileUpdate) -> ProfileRead:
        return self.repo.update(user_id, data)
