# notifications-service/tests/unit/test_notification_service.py
import uuid

from app.models.notification import (
    NotificationCreate,
    NotificationSettingsUpdate,
)
from app.services.notification_service import NotificationService
from app.repositories.notification_repository import NotificationRepository


class InMemoryNotificationRepository(NotificationRepository):
    def __init__(self):
        self._notifications: list[dict] = []
        self._settings: dict[str, dict] = {}

    # переопределим только то, что нужно для юнит-тестов
    def create_notification(self, data: NotificationCreate):
        obj = {
            "id": str(uuid.uuid4()),
            "user_id": str(data.user_id),
            "title": data.title,
            "body": data.body,
            "is_read": False,
        }
        self._notifications.append(obj)
        return type("Notification", (), obj)

    def list_notifications(self, user_id, include_read=True):
        filtered = [n for n in self._notifications if n["user_id"] == str(user_id)]
        return [type("Notification", (), n) for n in filtered]

    def mark_read(self, user_id, notification_ids=None):
        for n in self._notifications:
            if n["user_id"] == str(user_id):
                if notification_ids is None or n["id"] in map(str, notification_ids):
                    n["is_read"] = True

    def get_settings(self, user_id):
        if str(user_id) not in self._settings:
            return None
        return type("NotificationSettings", (), self._settings[str(user_id)])

    def upsert_settings(self, user_id, update_data: NotificationSettingsUpdate):
        data = self._settings.get(str(user_id), {
            "user_id": str(user_id),
            "enabled": True,
            "new_releases": True,
            "recommendations": True,
            "system": True,
        })
        for k, v in update_data.model_dump(exclude_unset=True).items():
            data[k] = v
        self._settings[str(user_id)] = data
        return type("NotificationSettings", (), data)


def test_create_and_list_notifications():
    repo = InMemoryNotificationRepository()
    svc = NotificationService(db=None)  # db не используется, репозиторий подменён
    svc.repo = repo

    user_id = uuid.uuid4()
    svc.create_notification(NotificationCreate(user_id=user_id, title="t", body="b"))
    svc.create_notification(NotificationCreate(user_id=user_id, title="t2", body="b2"))

    items = svc.list_notifications(user_id)
    assert len(items) == 2


def test_default_settings_and_update():
    repo = InMemoryNotificationRepository()
    svc = NotificationService(db=None)
    svc.repo = repo

    user_id = uuid.uuid4()
    s = svc.get_settings(user_id)
    assert s.enabled is True

    updated = svc.update_settings(
        user_id,
        NotificationSettingsUpdate(enabled=False, system=False),
    )
    assert updated.enabled is False
    assert updated.system is False
