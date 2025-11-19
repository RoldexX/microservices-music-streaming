# tests/integration/test_profile_http.py

import pytest
import socket
from uuid import uuid4

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db


def is_rabbitmq_available():
    """
    Универсальная проверка RabbitMQ:
    1. 'rabbitmq' — имя контейнера в docker-compose
    2. 'localhost'
    3. '127.0.0.1'
    """
    addresses = [
        ("rabbitmq", 5672),
        ("localhost", 5672),
        ("127.0.0.1", 5672),
    ]

    for host, port in addresses:
        try:
            with socket.create_connection((host, port), timeout=0.3):
                return True
        except OSError:
            continue

    return False


init_db()
client = TestClient(app)


def test_openapi_available():
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert "paths" in resp.json()


@pytest.mark.skipif(
    not is_rabbitmq_available(),
    reason="RabbitMQ недоступен, пропускаем тест.",
)
def test_create_profile_success():
    user_id = str(uuid4())

    resp = client.post(
        "/api/v1/internal/profiles",
        json={
            "user_id": user_id,
            "display_name": "TestUser",
            "region": "RU",
        },
    )

    assert 200 <= resp.status_code < 300, resp.text
    data = resp.json()
    assert data["user_id"] == user_id
    assert data["display_name"] == "TestUser"


@pytest.mark.skipif(
    not is_rabbitmq_available(),
    reason="RabbitMQ недоступен — невозможно создать профиль.",
)
def test_get_profile_success():
    user_id = str(uuid4())

    resp_create = client.post(
        "/api/v1/internal/profiles",
        json={
            "user_id": user_id,
            "display_name": "Example",
            "region": "EU",
        },
    )
    assert 200 <= resp_create.status_code < 300

    resp = client.get("/api/v1/profiles/me", params={"user_id": user_id})
    assert resp.status_code == 200
    assert resp.json()["region"] == "EU"


def test_get_profile_not_found():
    resp = client.get("/api/v1/profiles/me", params={"user_id": str(uuid4())})
    assert resp.status_code == 404
