# app/services/messaging.py
import json
import pika
from typing import Any, Dict

from app.settings import settings


class MessagingService:
    def __init__(self):
        self.url = settings.rabbitmq_url
        self.exchange = settings.rabbitmq_exchange

    def publish_event(self, routing_key: str, payload: Dict[str, Any]):
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

    def profile_created(self, user_id: str):
        self.publish_event(
            "profile.created",
            {"user_id": user_id}
        )
