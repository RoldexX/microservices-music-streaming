# app/schemas/profile.py
from uuid import uuid4
from sqlalchemy import Column, String, Boolean
from app.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, unique=True, nullable=False)

    display_name = Column(String, nullable=False)
    region = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    is_closed = Column(Boolean, default=False, nullable=False)
