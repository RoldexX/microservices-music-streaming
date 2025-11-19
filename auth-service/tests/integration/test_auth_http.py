# tests/integration/test_auth_flow.py

import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_openapi_and_docs_available():
    """
    Базовая проверка того, что приложение поднимается и схема/доки доступны.
    Это подтверждает корректную сборку FastAPI и регистрацию роутеров.
    """
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert "paths" in data

    resp = client.get("/docs")
    assert resp.status_code == 200


def test_register_and_login_flow():
    """
    Полный позитивный сценарий:
    - регистрация нового пользователя
    - успешный логин с теми же учётными данными
    """
    email = f"int_test_{uuid.uuid4().hex}@example.com"
    password = "StrongPass123!"

    # Регистрация
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "phone": "+70000000000",
            "password": password,
        },
    )
    assert resp.status_code == 200, resp.text
    reg_data = resp.json()
    assert "user_id" in reg_data

    # Логин
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
            "device_id": "test-device",
        },
    )
    assert resp.status_code == 200, resp.text
    tokens = resp.json()
    # структура токенов может отличаться, проверим базово
    assert "access_token" in tokens
    assert "refresh_token" in tokens or "refresh_token" in tokens.get("tokens", {})


def test_register_duplicate_email_returns_error():
    """
    Негативный сценарий:
    попытка зарегистрировать пользователя с уже существующим email
    должна вернуть ошибку 4xx.
    """
    email = f"dup_test_{uuid.uuid4().hex}@example.com"
    password = "StrongPass123!"

    # первая регистрация — успешная
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "phone": "+70000000000",
            "password": password,
        },
    )
    assert resp.status_code == 200, resp.text

    # вторая регистрация с тем же email — ошибка
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "phone": "+70000000000",
            "password": password,
        },
    )
    # в зависимости от реализации это может быть 400 или 409
    assert resp.status_code in (400, 409), resp.text
