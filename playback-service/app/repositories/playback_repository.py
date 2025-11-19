# app/repositories/playback_repository.py
from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session

from app.schemas.playback import PlaybackSession as PlaybackSessionORM
from app.models.playback import PlaybackStartRequest, PlaybackSessionRead, PlaybackStatus, SetVolumeRequest


class PlaybackRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _to_read(self, orm: PlaybackSessionORM) -> PlaybackSessionRead:
        return PlaybackSessionRead.model_validate(orm)

    def get_session(self, session_id: UUID | str) -> Optional[PlaybackSessionORM]:
        return (
            self.db.query(PlaybackSessionORM)
            .filter(PlaybackSessionORM.id == str(session_id))
            .first()
        )

    def create_session(self, data: PlaybackStartRequest) -> PlaybackSessionRead:
        row = PlaybackSessionORM(
            user_id=str(data.user_id),
            track_id=str(data.track_id),
            status=PlaybackStatus.PLAYING,
            position_sec=0,
            volume=data.volume,
            context_type=data.context_type,
            context_id=str(data.context_id) if data.context_id else None,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_read(row)

    def update_status(self, session_id: UUID | str, status: PlaybackStatus) -> PlaybackSessionRead:
        row = self.get_session(session_id)
        if not row:
            raise ValueError("Session not found")
        row.status = status
        row.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(row)
        return self._to_read(row)

    def set_volume(self, session_id: UUID | str, data: SetVolumeRequest) -> PlaybackSessionRead:
        row = self.get_session(session_id)
        if not row:
            raise ValueError("Session not found")
        row.volume = data.volume
        row.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(row)
        return self._to_read(row)

    def get_session_read(self, session_id: UUID | str) -> PlaybackSessionRead:
        row = self.get_session(session_id)
        if not row:
            raise ValueError("Session not found")
        return self._to_read(row)
