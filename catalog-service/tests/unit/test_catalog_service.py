# tests/unit/test_catalog_models.py

from uuid import uuid4
from datetime import date
from pydantic import ValidationError

from app.models.album import AlbumCreate
from app.models.track import TrackCreate


def test_album_create_valid():
    data = AlbumCreate(
        title="My Album",
        artist_name="Artist",
        release_date=date(2024, 1, 1),
        cover_url="https://example.com/cover.jpg",
    )
    assert data.title == "My Album"
    assert data.artist_name == "Artist"


def test_album_create_missing_fields():
    """Отсутствие обязательных полей вызывает ValidationError."""
    try:
        AlbumCreate(
            title=None,
            artist_name="Artist",
            release_date=None,
            cover_url=None
        )
    except ValidationError:
        assert True
    else:
        assert False, "ValidationError expected"


def test_track_create_valid():
    data = TrackCreate(
        title="Track 1",
        duration_sec=180,
        file_path="music/track1.mp3"
    )
    assert data.title == "Track 1"
    assert data.duration_sec == 180


def test_track_create_invalid_duration():
    try:
        TrackCreate(
            title="Track",
            duration_sec=-10,
            file_path="music/track.mp3"
        )
    except ValidationError:
        assert True
    else:
        assert False, "duration_sec < 0 — должно быть исключение"
