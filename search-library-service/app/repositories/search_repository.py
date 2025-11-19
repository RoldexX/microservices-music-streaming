# app/repositories/search_repository.py
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from app.schemas.search_item import SearchItem as SearchItemORM
from app.models.search import SearchItemRead


class SearchRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add_item(
        self,
        object_type: str,
        object_id: UUID | str,
        title: str,
        artist_name: str | None = None,
    ) -> SearchItemRead:
        row = SearchItemORM(
            object_type=object_type,
            object_id=str(object_id),
            title=title,
            artist_name=artist_name,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return SearchItemRead.model_validate(row)

    def search(
        self,
        query: str,
        type_filter: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[SearchItemRead]:
        q = self.db.query(SearchItemORM).filter(
            SearchItemORM.title.ilike(f"%{query}%")
        )
        if type_filter and type_filter in ("track", "album"):
            q = q.filter(SearchItemORM.object_type == type_filter)

        rows = q.offset(offset).limit(limit).all()
        return [SearchItemRead.model_validate(r) for r in rows]
