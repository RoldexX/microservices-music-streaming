# tests/integration/test_library_http.py

import socket
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db


def is_rabbitmq_available():
    """
    Проверяем RabbitMQ и в докере, и локально.
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


# инициализируем БД для тестов
init_db()
client = TestClient(app)


def test_openapi_available():
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert "paths" in resp.json()


@pytest.mark.skipif(
    not is_rabbitmq_available(),
    reason="RabbitMQ недоступен — создание плейлиста публикует событие, пропускаем.",
)
def test_create_playlist():
    """
    POST /api/v1/me/playlists?owner_id=
    """
    owner = uuid4()

    resp = client.post(
        "/api/v1/me/playlists",
        params={"owner_id": owner},
        json={"title": "Playlist A", "is_public": True},
    )

    assert 200 <= resp.status_code < 300, resp.text
    data = resp.json()
    assert data["title"] == "Playlist A"
    assert data["owner_id"] == str(owner)


def test_list_playlists_empty():
    owner = uuid4()

    resp = client.get("/api/v1/me/playlists", params={"owner_id": owner})

    assert resp.status_code == 200, resp.text
    assert resp.json() == []


@pytest.mark.skipif(
    not is_rabbitmq_available(),
    reason="RabbitMQ недоступен — добавление трека публикует событие, пропускаем.",
)
def test_add_track_to_playlist(monkeypatch):
    """
    Проверяем успешное добавление трека в плейлист,
    подменяя CatalogClient.get_track, чтобы не зависеть от catalog-service.
    """
    from app.services import catalog_client as catalog_client_module

    # Мокаем внешний HTTP-клиент: притворяемся, что трек существует в каталоге
    def fake_get_track(self, track_id: str):
        return {
            "id": track_id,
            "title": "Fake Track",
            "artist_name": "Fake Artist",
        }

    monkeypatch.setattr(
        catalog_client_module.CatalogClient,
        "get_track",
        fake_get_track,
        raising=True,
    )

    owner = uuid4()

    # 1) создаём плейлист
    create = client.post(
        "/api/v1/me/playlists",
        params={"owner_id": owner},
        json={"title": "Playlist X", "is_public": False},
    )
    assert 200 <= create.status_code < 300, create.text
    pid = create.json()["id"]

    # 2) добавляем трек — теперь CatalogClient всегда "находит" трек
    track_id = uuid4()

    resp = client.post(
        f"/api/v1/me/playlists/{pid}:add-track",
        params={"owner_id": owner},
        json={"track_id": str(track_id), "position": 0},
    )

    assert resp.status_code == 200, resp.text
    assert resp.json() == {"status": "ok"}


@pytest.mark.skipif(
    not is_rabbitmq_available(),
    reason="RabbitMQ недоступен — добавление избранного может публиковать событие, пропускаем.",
)
def test_add_favorite_track():
    owner = uuid4()
    track_id = uuid4()

    resp = client.post(
        "/api/v1/me/favorites/tracks",
        params={"owner_id": owner},
        json={"track_id": str(track_id)},
    )

    assert 200 <= resp.status_code < 300, resp.text
    data = resp.json()
    assert data["user_id"] == str(owner)
    assert data["track_id"] == str(track_id)


def test_list_favorite_tracks_empty():
    owner = uuid4()

    resp = client.get("/api/v1/me/favorites/tracks", params={"owner_id": owner})

    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)
    assert data == []
