# app/services/catalog_service.py
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.album import AlbumCreate, AlbumUpdate, AlbumRead
from app.models.track import TrackCreate, TrackUpdate, TrackRead
from app.repositories.catalog_repository import CatalogRepository
from app.services.messaging import MessagingService


class CatalogService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CatalogRepository(db)
        self.messaging = MessagingService()

    # ---------- ALBUMS ---------- #

    def create_album(self, data: AlbumCreate) -> AlbumRead:
        return self.repo.create_album(data)

    def get_album(self, album_id: UUID | str) -> AlbumRead:
        album_orm = self.repo.get_album(album_id)
        if not album_orm:
            raise ValueError("Album not found")
        return AlbumRead.model_validate(album_orm)

    def update_album(self, album_id: UUID | str, data: AlbumUpdate) -> AlbumRead:
        return self.repo.update_album(album_id, data)

    def publish_album(self, album_id: UUID | str) -> AlbumRead:
        album = self.repo.publish_album(album_id)
        # событие в RabbitMQ
        self.messaging.album_published(str(album.id))
        return album

    def list_albums(self, limit: int = 50, offset: int = 0) -> list[AlbumRead]:
        return self.repo.list_albums(limit=limit, offset=offset)

    # ---------- TRACKS ---------- #

    def create_track(self, album_id: UUID | str, data: TrackCreate) -> TrackRead:
        # проверим, что альбом существует
        album_orm = self.repo.get_album(album_id)
        if not album_orm:
            raise ValueError("Album not found")
        return self.repo.create_track(album_id, data)

    def get_track(self, track_id: UUID | str) -> TrackRead:
        track_orm = self.repo.get_track(track_id)
        if not track_orm:
            raise ValueError("Track not found")
        return TrackRead.model_validate(track_orm)

    def update_track(self, track_id: UUID | str, data: TrackUpdate) -> TrackRead:
        return self.repo.update_track(track_id, data)

    def publish_track(self, track_id: UUID | str) -> TrackRead:
        track = self.repo.publish_track(track_id)
        self.messaging.track_published(str(track.id), str(track.album_id))
        return track

    def list_tracks_by_album(self, album_id: UUID | str) -> list[TrackRead]:
        return self.repo.list_tracks_by_album(album_id)
