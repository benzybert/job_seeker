from __future__ import annotations

import json
import pika


def publish(host: str, queue_name: str, message: dict) -> None:
    params = pika.ConnectionParameters(host=host)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=json.dumps(message).encode("utf-8"),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    connection.close()


