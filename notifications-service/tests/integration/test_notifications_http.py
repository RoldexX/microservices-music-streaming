# tests/integration/test_notifications_http.py

import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
import app.database as db_module
from app.endpoints.notifications_router import router as notifications_router
from app.services.notification_service import NotificationService
from app.models.notification import NotificationCreate

# -----------------------------------------------------------------------------
# Инициализируем СВОЮ in-memory SQLite и подменяем get_db
# -----------------------------------------------------------------------------

# Делаем отдельный engine только для тестов
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаём все таблицы в in-memory БД
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------------------------------------------------------
# Собираем тестовое FastAPI-приложение (без app.main, чтобы не дергать init_db)
# -----------------------------------------------------------------------------

app = FastAPI()
app.include_router(notifications_router, prefix="/api/v1")

# Подменяем зависимость get_db, которую используют роуты
app.dependency_overrides[db_module.get_db] = override_get_db

client = TestClient(app)


# -----------------------------------------------------------------------------
#                         ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# -----------------------------------------------------------------------------

def test_notifications_settings_http():
    """Проверяем GET/PUT настроек уведомлений."""
    user_id = str(uuid.uuid4())

    # дефолтные настройки
    resp = client.get(
        "/api/v1/me/notifications/settings",
        params={"user_id": user_id},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["enabled"] is True

    # меняем настройки
    resp = client.put(
        "/api/v1/me/notifications/settings",
        params={"user_id": user_id},
        json={"enabled": False},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["enabled"] is False


def test_list_notifications_empty():
    """Для пользователя без уведомлений должен быть пустой список."""
    user_id = str(uuid.uuid4())

    resp = client.get(
        "/api/v1/me/notifications",
        params={"user_id": user_id},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data == []


def test_create_and_list_notifications_http():
    """
    Через NotificationService создаём уведомления в БД,
    затем читаем их через HTTP-эндпоинт.
    """
    user_id = uuid.uuid4()

    db = TestingSessionLocal()
    try:
        svc = NotificationService(db)
        svc.create_notification(
            NotificationCreate(
                user_id=user_id,
                title="Hello",
                body="First notification",
            )
        )
        svc.create_notification(
            NotificationCreate(
                user_id=user_id,
                title="Second",
                body="Second notification",
            )
        )
    finally:
        db.close()

    resp = client.get(
        "/api/v1/me/notifications",
        params={"user_id": str(user_id)},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 2
    titles = [n["title"] for n in data]
    assert "Hello" in titles and "Second" in titles


def test_mark_read_http():
    """
    Создаём два уведомления, одно помечаем прочитанным,
    проверяем include_read=False / True.
    """
    user_id = uuid.uuid4()

    db = TestingSessionLocal()
    try:
        svc = NotificationService(db)
        n1 = svc.create_notification(
            NotificationCreate(
                user_id=user_id,
                title="To read",
                body="Must be marked read",
            )
        )
        n2 = svc.create_notification(
            NotificationCreate(
                user_id=user_id,
                title="Stay unread",
                body="Should remain unread",
            )
        )
    finally:
        db.close()

    # помечаем первое как прочитанное
    resp = client.post(
        "/api/v1/me/notifications/mark-read",
        params={"user_id": str(user_id)},
        json={"notification_ids": [str(n1.id)]},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"status": "ok"}

    # include_read=False → только одно непрочитанное (n2)
    resp_unread = client.get(
        "/api/v1/me/notifications",
        params={"user_id": str(user_id), "include_read": False},
    )
    assert resp_unread.status_code == 200
    unread = resp_unread.json()
    assert len(unread) == 1
    assert unread[0]["title"] == "Stay unread"

    # include_read=True → оба
    resp_all = client.get(
        "/api/v1/me/notifications",
        params={"user_id": str(user_id), "include_read": True},
    )
    assert resp_all.status_code == 200
    all_items = resp_all.json()
    assert len(all_items) == 2
