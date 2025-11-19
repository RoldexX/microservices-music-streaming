# app/main.py
from fastapi import FastAPI

from app.database import init_db
from app.endpoints.playback_router import router as playback_router

app = FastAPI(title="Playback Service")

init_db()

app.include_router(playback_router, prefix="/api/v1")
