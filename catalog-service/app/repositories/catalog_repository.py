# app/repositories/catalog_repository.py
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.schemas.album import Album as AlbumORM
from app.schemas.track import Track as TrackORM
from app.models.album import AlbumCreate, AlbumUpdate, AlbumRead
from app.models.track import TrackCreate, TrackUpdate, TrackRead


class CatalogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # --------- ALBUMS --------- #

    def create_album(self, data: AlbumCreate) -> AlbumRead:
        album = AlbumORM(
            title=data.title,
            artist_name=data.artist_name,
            release_date=data.release_date,
            cover_url=str(data.cover_url) if data.cover_url else None,
            is_published=False,
        )
        self.db.add(album)
        self.db.commit()
        self.db.refresh(album)
        return AlbumRead.model_validate(album)

    def get_album(self, album_id: UUID | str) -> Optional[AlbumORM]:
        return self.db.query(AlbumORM).filter(AlbumORM.id == str(album_id)).first()

    def update_album(self, album_id: UUID | str, data: AlbumUpdate) -> AlbumRead:
        album = self.get_album(album_id)
        if not album:
            raise ValueError("Album not found")

        for key, value in data.model_dump(exclude_unset=True).items():
            if key == "cover_url" and value is not None:
                value = str(value)
            setattr(album, key, value)

        self.db.commit()
        self.db.refresh(album)
        return AlbumRead.model_validate(album)

    def publish_album(self, album_id: UUID | str) -> AlbumRead:
        album = self.get_album(album_id)
        if not album:
            raise ValueError("Album not found")

        album.is_published = True
        self.db.commit()
        self.db.refresh(album)
        return AlbumRead.model_validate(album)

    def list_albums(self, limit: int = 50, offset: int = 0) -> List[AlbumRead]:
        q = self.db.query(AlbumORM).offset(offset).limit(limit).all()
        return [AlbumRead.model_validate(a) for a in q]

    # --------- TRACKS --------- #

    def create_track(self, album_id: UUID | str, data: TrackCreate) -> TrackRead:
        track = TrackORM(
            album_id=str(album_id),
            title=data.title,
            duration_sec=data.duration_sec,
            file_path=data.file_path,
            is_published=False,
        )
        self.db.add(track)
        self.db.commit()
        self.db.refresh(track)
        return TrackRead.model_validate(track)

    def get_track(self, track_id: UUID | str) -> Optional[TrackORM]:
        return self.db.query(TrackORM).filter(TrackORM.id == str(track_id)).first()

    def update_track(self, track_id: UUID | str, data: TrackUpdate) -> TrackRead:
        track = self.get_track(track_id)
        if not track:
            raise ValueError("Track not found")

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(track, key, value)

        self.db.commit()
        self.db.refresh(track)
        return TrackRead.model_validate(track)

    def publish_track(self, track_id: UUID | str) -> TrackRead:
        track = self.get_track(track_id)
        if not track:
            raise ValueError("Track not found")

        track.is_published = True
        self.db.commit()
        self.db.refresh(track)
        return TrackRead.model_validate(track)

    def list_tracks_by_album(self, album_id: UUID | str) -> List[TrackRead]:
        rows = (
            self.db.query(TrackORM)
            .filter(TrackORM.album_id == str(album_id))
            .all()
        )
        return [TrackRead.model_validate(t) for t in rows]
