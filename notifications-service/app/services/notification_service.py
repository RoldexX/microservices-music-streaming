# app/services/notification_service.py
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.notification import (
    NotificationCreate,
    NotificationRead,
    NotificationSettingsRead,
    NotificationSettingsUpdate,
)
from app.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(self, db: Session) -> None:
        self.repo = NotificationRepository(db)

    # -------- Notifications -------- #

    def create_notification(self, data: NotificationCreate) -> NotificationRead:
        # Здесь можно было бы смотреть настройки, но для простоты мы создаём всегда.
        return self.repo.create_notification(data)

    def list_notifications(
        self,
        user_id: UUID | str,
        include_read: bool = True,
    ) -> list[NotificationRead]:
        return self.repo.list_notifications(user_id, include_read)

    def mark_read(
        self,
        user_id: UUID | str,
        notification_ids: list[UUID] | None = None,
    ) -> None:
        self.repo.mark_read(user_id, notification_ids)

    # -------- Settings -------- #

    def get_settings(self, user_id: UUID | str) -> NotificationSettingsRead:
        settings = self.repo.get_settings(user_id)
        if not settings:
            # если настроек нет — вернем значения по умолчанию (все включено)
            default = NotificationSettingsUpdate(
                enabled=True,
                new_releases=True,
                recommendations=True,
                system=True,
            )
            return self.repo.upsert_settings(user_id, default)
        return settings

    def update_settings(
        self,
        user_id: UUID | str,
        data: NotificationSettingsUpdate,
    ) -> NotificationSettingsRead:
        return self.repo.upsert_settings(user_id, data)
