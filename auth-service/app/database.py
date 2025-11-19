# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.settings import settings


class Base(DeclarativeBase):
    pass


# Для SQLite нужен параметр check_same_thread=False
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.schemas import user  # noqa: F401 — подгружаем модели

    Base.metadata.create_all(bind=engine)
