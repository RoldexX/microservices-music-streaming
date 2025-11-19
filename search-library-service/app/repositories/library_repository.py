# app/repositories/library_repository.py
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from app.schemas.playlist import Playlist as PlaylistORM, PlaylistTrack as PlaylistTrackORM
from app.schemas.favorite import FavoriteTrack as FavoriteTrackORM
from app.models.library import PlaylistCreate, PlaylistRead, PlaylistTrackCreate, FavoriteTrackRead


class LibraryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # -------- PLAYLISTS -------- #

    def create_playlist(self, owner_id: UUID | str, data: PlaylistCreate) -> PlaylistRead:
        pl = PlaylistORM(
            owner_id=str(owner_id),
            title=data.title,
            is_public=data.is_public,
        )
        self.db.add(pl)
        self.db.commit()
        self.db.refresh(pl)
        return PlaylistRead.model_validate(pl)

    def get_playlist(self, playlist_id: UUID | str) -> PlaylistORM | None:
        return self.db.query(PlaylistORM).filter(PlaylistORM.id == str(playlist_id)).first()

    def list_playlists(self, owner_id: UUID | str) -> List[PlaylistRead]:
        rows = self.db.query(PlaylistORM).filter(PlaylistORM.owner_id == str(owner_id)).all()
        return [PlaylistRead.model_validate(p) for p in rows]

    def add_track_to_playlist(
        self,
        playlist_id: UUID | str,
        data: PlaylistTrackCreate,
    ) -> None:
        # Определяем позицию: если не указана — берем последний +1
        if data.position is None:
            last = (
                self.db.query(PlaylistTrackORM)
                .filter(PlaylistTrackORM.playlist_id == str(playlist_id))
                .order_by(PlaylistTrackORM.position.desc())
                .first()
            )
            position = (last.position + 1) if last else 0
        else:
            position = data.position

        row = PlaylistTrackORM(
            playlist_id=str(playlist_id),
            track_id=str(data.track_id),
            position=position,
        )
        self.db.add(row)
        self.db.commit()

    # -------- FAVORITES -------- #

    def add_favorite_track(self, user_id: UUID | str, track_id: UUID | str) -> FavoriteTrackRead:
        fav = FavoriteTrackORM(
            user_id=str(user_id),
            track_id=str(track_id),
        )
        self.db.add(fav)
        self.db.commit()
        self.db.refresh(fav)
        return FavoriteTrackRead.model_validate(fav)

    def list_favorite_tracks(self, user_id: UUID | str) -> List[FavoriteTrackRead]:
        rows = (
            self.db.query(FavoriteTrackORM)
            .filter(FavoriteTrackORM.user_id == str(user_id))
            .all()
        )
        return [FavoriteTrackRead.model_validate(r) for r in rows]

    def remove_favorite_track(self, user_id: UUID | str, track_id: UUID | str) -> None:
        (
            self.db.query(FavoriteTrackORM)
            .filter(
                FavoriteTrackORM.user_id == str(user_id),
                FavoriteTrackORM.track_id == str(track_id),
            )
            .delete()
        )
        self.db.commit()
