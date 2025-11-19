# app/repositories/notification_repository.py
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.schemas.notification import Notification as NotificationORM
from app.schemas.settings import NotificationSettings as NotificationSettingsORM
from app.models.notification import (
    NotificationCreate,
    NotificationRead,
    NotificationSettingsRead,
    NotificationSettingsUpdate,
)


class NotificationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # -------- Notifications -------- #

    def create_notification(self, data: NotificationCreate) -> NotificationRead:
        row = NotificationORM(
            user_id=str(data.user_id),
            title=data.title,
            body=data.body,
            is_read=False,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return NotificationRead.model_validate(row)

    def list_notifications(
        self,
        user_id: UUID | str,
        include_read: bool = True,
    ) -> List[NotificationRead]:
        q = self.db.query(NotificationORM).filter(
            NotificationORM.user_id == str(user_id)
        )
        if not include_read:
            q = q.filter(NotificationORM.is_read == False)  # noqa: E712

        rows = q.order_by(NotificationORM.created_at.desc()).all()
        return [NotificationRead.model_validate(r) for r in rows]

    def mark_read(
        self,
        user_id: UUID | str,
        notification_ids: list[UUID] | None = None,
    ) -> None:
        q = self.db.query(NotificationORM).filter(
            NotificationORM.user_id == str(user_id)
        )
        if notification_ids:
            q = q.filter(NotificationORM.id.in_([str(nid) for nid in notification_ids]))
        q.update({NotificationORM.is_read: True})
        self.db.commit()

    # -------- Settings -------- #

    def get_settings(self, user_id: UUID | str) -> Optional[NotificationSettingsRead]:
        row = (
            self.db.query(NotificationSettingsORM)
            .filter(NotificationSettingsORM.user_id == str(user_id))
            .first()
        )
        if not row:
            return None
        return NotificationSettingsRead.model_validate(
            {
                "user_id": row.user_id,
                "enabled": row.enabled,
                "new_releases": row.new_releases,
                "recommendations": row.recommendations,
                "system": row.system,
            }
        )

    def upsert_settings(
        self,
        user_id: UUID | str,
        update_data: NotificationSettingsUpdate,
    ) -> NotificationSettingsRead:
        row = (
            self.db.query(NotificationSettingsORM)
            .filter(NotificationSettingsORM.user_id == str(user_id))
            .first()
        )
        if not row:
            row = NotificationSettingsORM(
                user_id=str(user_id),
            )
            self.db.add(row)

        data = update_data.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(row, key, value)

        self.db.commit()
        self.db.refresh(row)

        return NotificationSettingsRead.model_validate(
            {
                "user_id": row.user_id,
                "enabled": row.enabled,
                "new_releases": row.new_releases,
                "recommendations": row.recommendations,
                "system": row.system,
            }
        )
