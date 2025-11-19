# app/endpoints/playback_router.py
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.playback import (
    PlaybackStartRequest,
    PlaybackSessionRead,
    SetVolumeRequest,
    SimpleResponse,
)
from app.services.playback_service import PlaybackService

router = APIRouter(prefix="/playback", tags=["Playback"])


def service(db: Session = Depends(get_db)) -> PlaybackService:
    return PlaybackService(db)


@router.post("/start", response_model=PlaybackSessionRead)
def start_playback(
    data: PlaybackStartRequest,
    svc: PlaybackService = Depends(service),
):
    try:
        return svc.start(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{session_id}", response_model=PlaybackSessionRead)
def get_session(
    session_id: UUID,
    svc: PlaybackService = Depends(service),
):
    try:
        return svc.get_session(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{session_id}:pause", response_model=PlaybackSessionRead)
def pause(
    session_id: UUID,
    svc: PlaybackService = Depends(service),
):
    try:
        return svc.pause(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{session_id}:resume", response_model=PlaybackSessionRead)
def resume(
    session_id: UUID,
    svc: PlaybackService = Depends(service),
):
    try:
        return svc.resume(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{session_id}:stop", response_model=PlaybackSessionRead)
def stop(
    session_id: UUID,
    svc: PlaybackService = Depends(service),
):
    try:
        return svc.stop(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{session_id}:skip", response_model=PlaybackSessionRead)
def skip(
    session_id: UUID,
    svc: PlaybackService = Depends(service),
):
    try:
        return svc.skip(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{session_id}:set-volume", response_model=PlaybackSessionRead)
def set_volume(
    session_id: UUID,
    data: SetVolumeRequest,
    svc: PlaybackService = Depends(service),
):
    if not (0 <= data.volume <= 100):
        raise HTTPException(status_code=400, detail="Volume must be between 0 and 100")
    try:
        return svc.set_volume(session_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
