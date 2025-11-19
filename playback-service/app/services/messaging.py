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

    def track_started(self, session_id: str, user_id: str, track_id: str) -> None:
        self._publish(
            "playback.track.started",
            {
                "session_id": session_id,
                "user_id": user_id,
                "track_id": track_id,
            },
        )

    def track_finished(self, session_id: str, user_id: str, track_id: str) -> None:
        self._publish(
            "playback.track.finished",
            {
                "session_id": session_id,
                "user_id": user_id,
                "track_id": track_id,
            },
        )
