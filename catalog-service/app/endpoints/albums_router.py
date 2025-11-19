# app/endpoints/albums_router.py
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.album import AlbumCreate, AlbumUpdate, AlbumRead
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/albums", tags=["Albums"])


def service(db: Session = Depends(get_db)) -> CatalogService:
    return CatalogService(db)


@router.post("/", response_model=AlbumRead)
def create_album(
    data: AlbumCreate,
    svc: CatalogService = Depends(service),
):
    return svc.create_album(data)


@router.get("/", response_model=List[AlbumRead])
def list_albums(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    svc: CatalogService = Depends(service),
):
    return svc.list_albums(limit=limit, offset=offset)


@router.get("/{album_id}", response_model=AlbumRead)
def get_album(
    album_id: UUID,
    svc: CatalogService = Depends(service),
):
    try:
        return svc.get_album(album_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{album_id}", response_model=AlbumRead)
def update_album(
    album_id: UUID,
    data: AlbumUpdate,
    svc: CatalogService = Depends(service),
):
    try:
        return svc.update_album(album_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{album_id}:publish", response_model=AlbumRead)
def publish_album(
    album_id: UUID,
    svc: CatalogService = Depends(service),
):
    try:
        return svc.publish_album(album_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
