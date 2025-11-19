# app/schemas/__init__.py
# Импортируем модели, чтобы Base.metadata.create_all их "видел"
from .user import User  # noqa: F401
