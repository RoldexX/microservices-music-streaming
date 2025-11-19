# app/schemas/playlist.py
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from app.database import Base


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    owner_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)


class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    playlist_id = Column(String, ForeignKey("playlists.id"), nullable=False)
    track_id = Column(String, nullable=False)
    position = Column(Integer, nullable=False, default=0)
