# app/worker.py
import json
import time
import sys

import pika
from sqlalchemy.orm import Session

from app.settings import settings
from app.database import SessionLocal
from app.models.notification import NotificationCreate
from app.services.notification_service import NotificationService


def handle_message(body: bytes) -> None:
    """
    Простейшая обработка события.
    Ожидаем JSON с полями:
    - user_id или owner_id
    """
    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        return

    user_id = payload.get("user_id") or payload.get("owner_id")
    if not user_id:
        return

    title = "Уведомление"
    body_text = json.dumps(payload, ensure_ascii=False)

    db: Session = SessionLocal()
    try:
        svc = NotificationService(db)
        data = NotificationCreate(
            user_id=user_id,
            title=title,
            body=body_text,
        )
        svc.create_notification(data)
    finally:
        db.close()


def create_channel_with_retry(max_retries: int | None = None, delay_sec: int = 5):
    """
    Подключаемся к RabbitMQ с ретраями.
    max_retries = None -> бесконечно пытаемся.
    """
    attempt = 0
    while True:
        attempt += 1
        try:
            print(
                f"[worker] Connecting to RabbitMQ {settings.rabbitmq_url} "
                f"(attempt {attempt})",
                flush=True,
            )
            connection = pika.BlockingConnection(
                pika.URLParameters(settings.rabbitmq_url)
            )
            channel = connection.channel()
            return connection, channel
        except pika.exceptions.AMQPConnectionError as e:
            print(
                f"[worker] RabbitMQ not ready yet: {e}. "
                f"Retry in {delay_sec} sec...",
                flush=True,
            )
            if max_retries is not None and attempt >= max_retries:
                print("[worker] Max retries exceeded, exiting", flush=True)
                sys.exit(1)
            time.sleep(delay_sec)


def consume() -> None:
    connection, channel = create_channel_with_retry()

    channel.exchange_declare(
        exchange=settings.rabbitmq_exchange,
        exchange_type="topic",
        durable=True,
    )

    channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)

    for binding_key in settings.rabbitmq_binding_keys:
        channel.queue_bind(
            exchange=settings.rabbitmq_exchange,
            queue=settings.rabbitmq_queue,
            routing_key=binding_key,
        )

    def callback(ch, method, properties, body):
        handle_message(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=settings.rabbitmq_queue,
        on_message_callback=callback,
    )

    print(" [*] Notifications worker started. Waiting for messages...", flush=True)
    channel.start_consuming()


def main():
    consume()


if __name__ == "__main__":
    main()
