# app/endpoints/tracks_router.py
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.track import TrackCreate, TrackUpdate, TrackRead
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/tracks", tags=["Tracks"])


def service(db: Session = Depends(get_db)) -> CatalogService:
    return CatalogService(db)


@router.post("/albums/{album_id}", response_model=TrackRead)
def create_track(
    album_id: UUID,
    data: TrackCreate,
    svc: CatalogService = Depends(service),
):
    try:
        return svc.create_track(album_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{track_id}", response_model=TrackRead)
def get_track(
    track_id: UUID,
    svc: CatalogService = Depends(service),
):
    try:
        return svc.get_track(track_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{track_id}", response_model=TrackRead)
def update_track(
    track_id: UUID,
    data: TrackUpdate,
    svc: CatalogService = Depends(service),
):
    try:
        return svc.update_track(track_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{track_id}:publish", response_model=TrackRead)
def publish_track(
    track_id: UUID,
    svc: CatalogService = Depends(service),
):
    try:
        return svc.publish_track(track_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/albums/{album_id}", response_model=List[TrackRead])
def list_tracks_by_album(
    album_id: UUID,
    svc: CatalogService = Depends(service),
):
    return svc.list_tracks_by_album(album_id)
