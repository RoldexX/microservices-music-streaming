# app/services/playback_service.py
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.playback import (
    PlaybackStartRequest,
    PlaybackSessionRead,
    PlaybackStatus,
    SetVolumeRequest,
)
from app.repositories.playback_repository import PlaybackRepository
from app.services.catalog_client import CatalogClient
from app.services.messaging import MessagingService


class PlaybackService:
    def __init__(self, db: Session) -> None:
        self.repo = PlaybackRepository(db)
        self.catalog_client = CatalogClient()
        self.messaging = MessagingService()

    def start(self, data: PlaybackStartRequest) -> PlaybackSessionRead:
        # Проверяем трек в catalog-service
        track = self.catalog_client.get_track(str(data.track_id))
        if not track:
            raise ValueError("Track not found in catalog")

        session = self.repo.create_session(data)

        # Событие "старт воспроизведения"
        self.messaging.track_started(
            session_id=str(session.id),
            user_id=str(session.user_id),
            track_id=str(session.track_id),
        )
        return session

    def get_session(self, session_id: UUID | str) -> PlaybackSessionRead:
        return self.repo.get_session_read(session_id)

    def pause(self, session_id: UUID | str) -> PlaybackSessionRead:
        return self.repo.update_status(session_id, PlaybackStatus.PAUSED)

    def resume(self, session_id: UUID | str) -> PlaybackSessionRead:
        return self.repo.update_status(session_id, PlaybackStatus.PLAYING)

    def stop(self, session_id: UUID | str) -> PlaybackSessionRead:
        # Здесь считаем stop == finished для простоты
        session = self.repo.update_status(session_id, PlaybackStatus.FINISHED)
        self.messaging.track_finished(
            session_id=str(session.id),
            user_id=str(session.user_id),
            track_id=str(session.track_id),
        )
        return session

    def skip(self, session_id: UUID | str) -> PlaybackSessionRead:
        # Аналогично stop — завершение текущего трека
        return self.stop(session_id)

    def set_volume(self, session_id: UUID | str, data: SetVolumeRequest) -> PlaybackSessionRead:
        return self.repo.set_volume(session_id, data)
