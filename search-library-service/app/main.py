# app/main.py
from fastapi import FastAPI

from app.database import init_db
from app.endpoints.search_router import router as search_router
from app.endpoints.library_router import router as library_router

app = FastAPI(title="Search & Library Service")

init_db()

app.include_router(search_router, prefix="/api/v1")
app.include_router(library_router, prefix="/api/v1")
