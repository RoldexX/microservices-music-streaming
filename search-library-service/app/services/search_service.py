# app/services/search_service.py
from sqlalchemy.orm import Session

from app.models.search import SearchResponse
from app.repositories.search_repository import SearchRepository


class SearchService:
    def __init__(self, db: Session) -> None:
        self.repo = SearchRepository(db)

    def search(self, query: str, type_filter: str | None = None) -> SearchResponse:
        items = self.repo.search(query=query, type_filter=type_filter)
        return SearchResponse(
            query=query,
            type=type_filter or "all",
            items=items,
        )
