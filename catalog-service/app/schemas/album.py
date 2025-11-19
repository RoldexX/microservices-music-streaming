# app/schemas/album.py
from uuid import uuid4

from sqlalchemy import Column, String, Boolean, Date
from app.database import Base


class Album(Base):
    __tablename__ = "albums"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    title = Column(String, nullable=False)
    artist_name = Column(String, nullable=False)
    release_date = Column(Date, nullable=True)
    cover_url = Column(String, nullable=True)
    is_published = Column(Boolean, default=False, nullable=False)
