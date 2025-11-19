# app/schemas/settings.py
from uuid import uuid4

from sqlalchemy import Column, String, Boolean

from app.database import Base


class NotificationSettings(Base):
    __tablename__ = "notification_settings"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, unique=True, nullable=False)

    enabled = Column(Boolean, default=True, nullable=False)
    new_releases = Column(Boolean, default=True, nullable=False)
    recommendations = Column(Boolean, default=True, nullable=False)
    system = Column(Boolean, default=True, nullable=False)
