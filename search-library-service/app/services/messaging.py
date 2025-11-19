# app/services/messaging.py
import json
from typing import Any, Dict

import pika

from app.settings import settings


class MessagingService:
    def __init__(self) -> None:
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

        body = json.dumps(payload, default=str).encode("utf-8")

        channel.basic_publish(
            exchange=self.exchange,
            routing_key=routing_key,
            body=body,
        )

        connection.close()

    def playlist_created(self, playlist_id: str, owner_id: str) -> None:
        self._publish(
            "library.playlist.created",
            {"playlist_id": playlist_id, "owner_id": owner_id},
        )

    def playlist_track_added(self, playlist_id: str, track_id: str, owner_id: str) -> None:
        self._publish(
            "library.playlist.track_added",
            {
                "playlist_id": playlist_id,
                "track_id": track_id,
                "owner_id": owner_id,
            },
        )
