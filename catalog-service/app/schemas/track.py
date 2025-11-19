# app/schemas/track.py
from uuid import uuid4

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from app.database import Base


class Track(Base):
    __tablename__ = "tracks"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    album_id = Column(String, ForeignKey("albums.id"), nullable=False)

    title = Column(String, nullable=False)
    duration_sec = Column(Integer, nullable=False)
    file_path = Column(String, nullable=True)
    is_published = Column(Boolean, default=False, nullable=False)
