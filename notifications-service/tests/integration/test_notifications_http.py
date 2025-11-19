# tests/integration/test_notifications_http.py

import uuid

from fastapi.testclient import TestClient

# ВАЖНО: сначала переопределяем DATABASE_URL, потом импортируем app.main
from app import settings
settings.DATABASE_URL = "sqlite:///:memory:"

from app.main import app  # здесь внутри уже вызовется init_db с in-memory БД

client = TestClient(app)


def test_notifications_settings_flow():
    """Проверяем дефолтные настройки и обновление enabled."""
    user_id = str(uuid.uuid4())

    # дефолт
    resp = client.get(
        "/api/v1/me/notifications/settings",
        params={"user_id": user_id},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "enabled" in data

    # обновляем
    resp = client.put(
        "/api/v1/me/notifications/settings",
        params={"user_id": user_id},
        json={"enabled": False},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["enabled"] is False


def test_list_notifications_empty():
    """Новый пользователь — список уведомлений пустой."""
    user_id = str(uuid.uuid4())

    resp = client.get(
        "/api/v1/me/notifications",
        params={"user_id": user_id},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data == []


def test_mark_read_empty_ok():
    """
    Помечаем прочитанными пустой список уведомлений —
    сервис не должен падать, должен вернуть 200.
    """
    user_id = str(uuid.uuid4())

    resp = client.post(
        "/api/v1/me/notifications/mark-read",
        params={"user_id": user_id},
        json={"notification_ids": []},
    )
    assert resp.status_code == 200
    # дальше можно просто проверить, что это какой-то JSON-объект
    body = resp.json()
    assert isinstance(body, dict)
