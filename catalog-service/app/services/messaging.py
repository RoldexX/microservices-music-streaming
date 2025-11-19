# app/services/messaging.py
import json
from typing import Any, Dict

import pika

from app.settings import settings


class MessagingService:
    def __init__(self):
        self.url = settings.rabbitmq_url
        self.exchange = settings.rabbitmq_exchange

    def _publish(self, routing_key: str, payload: Dict[str, Any]) -> None:
        connection = pika.BlockingConnection(pika.URLParameters(self.url))
        channel = connection.channel()

        channel.exchange_declare(
            exchange=self.exchange,
            exchange_type="topic",
            durable=True,
        )

        channel.basic_publish(
            exchange=self.exchange,
            routing_key=routing_key,
            body=json.dumps(payload, default=str),
        )

        connection.close()

    def album_published(self, album_id: str) -> None:
        self._publish(
            "catalog.album.published",
            {"album_id": album_id},
        )

    def track_published(self, track_id: str, album_id: str) -> None:
        self._publish(
            "catalog.track.published",
            {"track_id": track_id, "album_id": album_id},
        )
