# tests/unit/test_library_models.py

from uuid import uuid4
from app.models.library import (
    PlaylistCreate,
    PlaylistTrackCreate,
    FavoriteTrackCreate,
)
from app.models.search import SearchItemBase, SearchResponse


def test_playlist_create():
    m = PlaylistCreate(title="My Playlist", is_public=True)
    assert m.title == "My Playlist"
    assert m.is_public is True


def test_playlist_track_create():
    tid = uuid4()
    m = PlaylistTrackCreate(track_id=tid, position=3)
    assert m.track_id == tid
    assert m.position == 3


def test_playlist_track_default_position():
    tid = uuid4()
    m = PlaylistTrackCreate(track_id=tid)
    assert m.track_id == tid
    assert m.position is None  # дефолт именно такой


def test_favorite_track_create():
    tid = uuid4()
    fav = FavoriteTrackCreate(track_id=tid)
    assert fav.track_id == tid


def test_search_item_base():
    obj = SearchItemBase(
        object_type="track",
        object_id=uuid4(),
        title="Song",
        artist_name="Artist",
    )
    assert obj.object_type == "track"
    assert obj.title == "Song"


def test_search_response_basic():
    r = SearchResponse(
        query="rock",
        type="all",
        items=[]
    )
    assert r.query == "rock"
    assert isinstance(r.items, list)
