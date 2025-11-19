# app/main.py
from fastapi import FastAPI

from app.database import init_db
from app.endpoints.notifications_router import router as notifications_router

app = FastAPI(title="Notifications Service")

init_db()

app.include_router(notifications_router, prefix="/api/v1")
