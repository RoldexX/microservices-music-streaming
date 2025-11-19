# tests/integration/test_catalog_http.py

from uuid import uuid4
from datetime import date

from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db

# Создаём таблицы
init_db()

client = TestClient(app)


def test_openapi_available():
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert "paths" in resp.json()


def test_create_album_success():
    """Создаём альбом через /albums."""
    resp = client.post(
        "/api/v1/albums",
        json={
            "title": "Album Test",
            "artist_name": "Test Artist",
            "release_date": "2024-01-01",
            "cover_url": None
        },
    )

    assert 200 <= resp.status_code < 300, resp.text
    data = resp.json()
    assert data["title"] == "Album Test"
    assert data["artist_name"] == "Test Artist"


def test_create_album_invalid():
    """Некорректные данные должны вызвать 422."""
    resp = client.post(
        "/api/v1/albums",
        json={"artist_name": "Artist"},  # нет title
    )
    assert resp.status_code == 422


def test_create_track_success():
    """Создаём трек внутри альбома."""
    # 1) создаем альбом
    album_resp = client.post(
        "/api/v1/albums",
        json={
            "title": "Album1",
            "artist_name": "Artist1",
            "release_date": "2024-01-01",
            "cover_url": None
        },
    )
    assert 200 <= album_resp.status_code < 300
    album_id = album_resp.json()["id"]

    # 2) создаём трек внутри альбома
    track_resp = client.post(
        f"/api/v1/tracks/albums/{album_id}",
        json={
            "title": "Track A",
            "duration_sec": 120,
            "file_path": "music/trackA.mp3"
        },
    )
    assert 200 <= track_resp.status_code < 300, track_resp.text

    track = track_resp.json()
    assert track["title"] == "Track A"
    assert track["album_id"] == album_id


def test_get_album_success():
    """Проверяем, что можно прочитать альбом после создания."""
    # создаем альбом
    resp_create = client.post(
        "/api/v1/albums",
        json={
            "title": "Read Album",
            "artist_name": "Artist",
            "release_date": "2024-01-01",
            "cover_url": None
        },
    )
    assert 200 <= resp_create.status_code < 300

    album_id = resp_create.json()["id"]

    # читаем альбом
    resp = client.get(f"/api/v1/albums/{album_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Read Album"


def test_get_album_not_found():
    resp = client.get(f"/api/v1/albums/{uuid4()}")
    assert resp.status_code == 404
