# app/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # SQLite
    database_url: str = "sqlite:///./data/notifications.db"

    # RabbitMQ
    rabbitmq_url: str = "amqp://rmuser:rmpass@localhost:5672/"
    rabbitmq_exchange: str = "music.events"
    rabbitmq_queue: str = "notifications-queue"

    # Какие ключи слушаем
    rabbitmq_binding_keys: list[str] = [
        "auth.user.registered",
        "catalog.album.published",
        "catalog.track.published",
        "library.playlist.created",
        "library.playlist.track_added",
        "playback.track.finished",
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
