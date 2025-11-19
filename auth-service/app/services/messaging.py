# app/services/messaging.py
import json
from typing import Any, Dict

import pika

from app.settings import settings


class MessagingService:
    """
    Простой синхронный паблишер в RabbitMQ.
    Открывает соединение, публикует сообщение, закрывает соединение.
    Для учебной работы достаточно.
    """

    def __init__(
        self,
        rabbitmq_url: str | None = None,
        exchange: str | None = None,
    ) -> None:
        self.rabbitmq_url = rabbitmq_url or settings.rabbitmq_url
        self.exchange = exchange or settings.rabbitmq_exchange

    def publish_event(self, routing_key: str, payload: Dict[str, Any]) -> None:
        connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
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
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,  # persistent
            ),
        )

        connection.close()

    # Удобный метод именно для события регистрации пользователя
    def publish_user_registered(self, user_id: str, email: str) -> None:
        self.publish_event(
            routing_key="auth.user.registered",
            payload={
                "user_id": user_id,
                "email": email,
            },
        )
