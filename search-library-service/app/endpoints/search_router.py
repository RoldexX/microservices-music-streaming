# app/endpoints/search_router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.search import SearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search"])


def service(db: Session = Depends(get_db)) -> SearchService:
    return SearchService(db)


@router.get("/", response_model=SearchResponse)
def search(
    query: str = Query(..., min_length=1),
    type: str | None = Query(None, pattern="^(track|album|all)$"),
    db: Session = Depends(get_db),
):
    svc = SearchService(db)
    type_filter = None if type in (None, "all") else type
    return svc.search(query=query, type_filter=type_filter)
