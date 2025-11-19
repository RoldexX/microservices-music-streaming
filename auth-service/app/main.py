# app/main.py
from fastapi import FastAPI

from app.database import init_db
from app.endpoints.auth_router import router as auth_router

app = FastAPI(title="Auth Service")

# создаем таблицы при старте (для учебной работы ок)
init_db()

app.include_router(auth_router, prefix="/api/v1")
