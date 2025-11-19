# app/schemas/favorite.py
from uuid import uuid4

from sqlalchemy import Column, String
from app.database import Base


class FavoriteTrack(Base):
    __tablename__ = "favorite_tracks"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, nullable=False)
    track_id = Column(String, nullable=False)
