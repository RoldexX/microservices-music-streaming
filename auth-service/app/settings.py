# app/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # SQLite
    database_url: str = "sqlite:///./auth.db"

    # JWT
    secret_key: str = "change_me_in_env"  # для учебы так сойдет, в бою обязательно менять
    access_token_expires_minutes: int = 60
    refresh_token_expires_days: int = 7
    jwt_algorithm: str = "HS256"

    # RabbitMQ
    rabbitmq_url: str = "amqp://rmuser:rmpass@localhost:5672/"
    rabbitmq_exchange: str = "music.events"

    # Profile service (синхронное взаимодействие)
    profile_service_base_url: str = "http://localhost:8001/api/v1"  # profile-service:8001

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
