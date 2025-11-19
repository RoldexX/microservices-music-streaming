# app/main.py
from fastapi import FastAPI

from app.database import init_db
from app.endpoints.albums_router import router as albums_router
from app.endpoints.tracks_router import router as tracks_router

app = FastAPI(title="Catalog Service")

init_db()

app.include_router(albums_router, prefix="/api/v1")
app.include_router(tracks_router, prefix="/api/v1")
