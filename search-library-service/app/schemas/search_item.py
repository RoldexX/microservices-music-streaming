# app/schemas/search_item.py
from uuid import uuid4

from sqlalchemy import Column, String
from app.database import Base


class SearchItem(Base):
    __tablename__ = "search_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    object_type = Column(String, nullable=False)  # 'track' или 'album'
    object_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    artist_name = Column(String, nullable=True)
