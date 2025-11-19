# app/endpoints/library_router.py
from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.library import (
    PlaylistCreate,
    PlaylistRead,
    PlaylistTrackCreate,
    FavoriteTrackCreate,
    FavoriteTrackRead,
)
from app.services.library_service import LibraryService

router = APIRouter(prefix="/me", tags=["Library"])


def service(db: Session = Depends(get_db)) -> LibraryService:
    return LibraryService(db)


# -------- PLAYLISTS -------- #

@router.post("/playlists", response_model=PlaylistRead)
def create_playlist(
    owner_id: UUID,
    data: PlaylistCreate,
    svc: LibraryService = Depends(service),
):
    return svc.create_playlist(owner_id, data)


@router.get("/playlists", response_model=List[PlaylistRead])
def list_playlists(
    owner_id: UUID,
    svc: LibraryService = Depends(service),
):
    return svc.list_playlists(owner_id)


@router.post("/playlists/{playlist_id}:add-track")
def add_track_to_playlist(
    owner_id: UUID,
    playlist_id: UUID,
    data: PlaylistTrackCreate,
    svc: LibraryService = Depends(service),
):
    try:
        svc.add_track_to_playlist(owner_id, playlist_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok"}


# -------- FAVORITES -------- #

@router.post("/favorites/tracks", response_model=FavoriteTrackRead)
def add_favorite_track(
    owner_id: UUID,
    data: FavoriteTrackCreate,
    svc: LibraryService = Depends(service),
):
    return svc.add_favorite_track(owner_id, data)


@router.get("/favorites/tracks", response_model=List[FavoriteTrackRead])
def list_favorites_tracks(
    owner_id: UUID,
    svc: LibraryService = Depends(service),
):
    return svc.list_favorite_tracks(owner_id)


@router.delete("/favorites/tracks/{track_id}")
def remove_favorite_track(
    owner_id: UUID,
    track_id: UUID,
    svc: LibraryService = Depends(service),
):
    svc.remove_favorite_track(owner_id, track_id)
    return {"status": "ok"}
