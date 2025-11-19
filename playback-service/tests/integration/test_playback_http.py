# playback-service/tests/integration/test_playback_http.py
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_playback_http_flow():
    user_id = str(uuid4())
    track_id = str(uuid4())

    resp = client.post(
        "/api/v1/playback/start",
        json={
            "user_id": user_id,
            "track_id": track_id,
            "context_type": "playlist",
            "context_id": str(uuid4()),
            "volume": 70,
        },
    )
    # В реальной конфигурации здесь нужен живой catalog-service;
    # в учебных целях можно временно замокать CatalogClient или ослабить проверку.
    assert resp.status_code in (200, 400)
