# app/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # SQLite
    database_url: str = "sqlite:///./profile.db"

    # RabbitMQ
    rabbitmq_url: str = "amqp://rmuser:rmpass@localhost:5672/"
    rabbitmq_exchange: str = "music.events"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
