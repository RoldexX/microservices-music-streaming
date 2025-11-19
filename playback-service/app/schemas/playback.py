# app/schemas/playback.py
from uuid import uuid4
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Enum as SAEnum

from app.database import Base
from app.models.playback import PlaybackStatus


class PlaybackSession(Base):
    __tablename__ = "playback_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=False)
    track_id = Column(String, nullable=False)

    status = Column(SAEnum(PlaybackStatus), default=PlaybackStatus.PLAYING, nullable=False)
    position_sec = Column(Integer, default=0, nullable=False)
    volume = Column(Integer, default=50, nullable=False)

    context_type = Column(String, nullable=True)
    context_id = Column(String, nullable=True)

    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
