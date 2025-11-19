# app/main.py
from fastapi import FastAPI

from app.database import init_db
from app.endpoints.profile_router import router as profile_router
from app.endpoints.internal_router import router as internal_router

app = FastAPI(title="Profile Service")

init_db()

app.include_router(profile_router, prefix="/api/v1")
app.include_router(internal_router, prefix="/api/v1")
