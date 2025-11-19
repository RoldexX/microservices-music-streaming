# playback-service/tests/unit/test_playback_service.py
import uuid

import pytest

from app.models.playback import PlaybackStartRequest, SetVolumeRequest, PlaybackStatus
from app.services.playback_service import PlaybackService
from app.repositories.playback_repository import PlaybackRepository


class InMemoryPlaybackRepository(PlaybackRepository):
    def __init__(self):
        self._sessions: dict[str, dict] = {}

    def create_session(self, data: PlaybackStartRequest):
        sid = str(uuid.uuid4())
        self._sessions[sid] = {
            "id": sid,
            "user_id": str(data.user_id),
            "track_id": str(data.track_id),
            "status": PlaybackStatus.PLAYING,
            "position_sec": 0,
            "volume": data.volume,
            "context_type": data.context_type,
            "context_id": str(data.context_id) if data.context_id else None,
        }
        return type("Session", (), self._sessions[sid])

    def get_session(self, session_id):
        if str(session_id) not in self._sessions:
            return None
        return type("Session", (), self._sessions[str(session_id)])

    def update_status(self, session_id, status: PlaybackStatus):
        self._sessions[str(session_id)]["status"] = status
        return type("Session", (), self._sessions[str(session_id)])

    def set_volume(self, session_id, data: SetVolumeRequest):
        self._sessions[str(session_id)]["volume"] = data.volume
        return type("Session", (), self._sessions[str(session_id)])


class DummyCatalogClient:
    def get_track(self, track_id: str):
        return {"id": track_id, "title": "dummy"}


class DummyMessaging:
    def __init__(self):
        self.started = []
        self.finished = []

    def track_started(self, session_id, user_id, track_id):
        self.started.append((session_id, user_id, track_id))

    def track_finished(self, session_id, user_id, track_id):
        self.finished.append((session_id, user_id, track_id))


@pytest.fixture
def playback_service():
    repo = InMemoryPlaybackRepository()
    svc = PlaybackService(db=None)
    svc.repo = repo
    svc.catalog_client = DummyCatalogClient()
    svc.messaging = DummyMessaging()
    return svc


def test_start_and_stop(playback_service):
    user_id = uuid.uuid4()
    track_id = uuid.uuid4()

    session = playback_service.start(
        PlaybackStartRequest(
            user_id=user_id,
            track_id=track_id,
            context_type="playlist",
            context_id=uuid.uuid4(),
            volume=70,
        )
    )
    assert session.status == PlaybackStatus.PLAYING

    stopped = playback_service.stop(session.id)
    assert stopped.status == PlaybackStatus.FINISHED
    assert len(playback_service.messaging.started) == 1
    assert len(playback_service.messaging.finished) == 1


def test_set_volume(playback_service):
    user_id = uuid.uuid4()
    track_id = uuid.uuid4()

    session = playback_service.start(
        PlaybackStartRequest(
            user_id=user_id,
            track_id=track_id,
            context_type=None,
            context_id=None,
            volume=50,
        )
    )
    updated = playback_service.set_volume(
        session.id,
        SetVolumeRequest(volume=10),
    )
    assert updated.volume == 10
