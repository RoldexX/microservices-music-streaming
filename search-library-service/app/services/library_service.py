# app/services/library_service.py
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.library import (
    PlaylistCreate,
    PlaylistRead,
    PlaylistTrackCreate,
    FavoriteTrackCreate,
    FavoriteTrackRead,
)
from app.repositories.library_repository import LibraryRepository
from app.services.catalog_client import CatalogClient
from app.services.messaging import MessagingService


class LibraryService:
    """
    Бизнес-логика библиотеки пользователя.
    Важный момент: при добавлении трека в плейлист вызываем catalog-service,
    чтобы убедиться, что трек существует.
    """

    def __init__(self, db: Session) -> None:
        self.repo = LibraryRepository(db)
        self.catalog_client = CatalogClient()
        self.messaging = MessagingService()

    # -------- PLAYLISTS -------- #

    def create_playlist(self, owner_id: UUID | str, data: PlaylistCreate) -> PlaylistRead:
        playlist = self.repo.create_playlist(owner_id, data)
        # Публикуем событие
        self.messaging.playlist_created(str(playlist.id), str(playlist.owner_id))
        return playlist

    def list_playlists(self, owner_id: UUID | str) -> list[PlaylistRead]:
        return self.repo.list_playlists(owner_id)

    def add_track_to_playlist(
        self,
        owner_id: UUID | str,
        playlist_id: UUID | str,
        data: PlaylistTrackCreate,
    ) -> None:
        # Вложенный вызов: сначала проверка существования трека через catalog-service
        track = self.catalog_client.get_track(str(data.track_id))
        if not track:
            raise ValueError("Track not found in catalog")

        # Затем добавляем в плейлист в нашей БД
        self.repo.add_track_to_playlist(playlist_id, data)

        # Публикуем событие
        self.messaging.playlist_track_added(
            playlist_id=str(playlist_id),
            track_id=str(data.track_id),
            owner_id=str(owner_id),
        )

    # -------- FAVORITES -------- #

    def add_favorite_track(
        self,
        user_id: UUID | str,
        data: FavoriteTrackCreate,
    ) -> FavoriteTrackRead:
        # Опционально тоже можем проверить трек в catalog-service,
        # но для краткости тут не делаем.
        fav = self.repo.add_favorite_track(user_id, data.track_id)
        return fav

    def list_favorite_tracks(self, user_id: UUID | str) -> list[FavoriteTrackRead]:
        return self.repo.list_favorite_tracks(user_id)

    def remove_favorite_track(self, user_id: UUID | str, track_id: UUID | str) -> None:
        self.repo.remove_favorite_track(user_id, track_id)
