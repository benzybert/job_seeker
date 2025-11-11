from __future__ import annotations

import json
import pika
from typing import Callable


def consume(host: str, queue_name: str, handler: Callable[[dict], None]) -> None:
    params = pika.ConnectionParameters(host=host)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    def _callback(ch, method, properties, body):
        msg = json.loads(body.decode("utf-8"))
        handler(msg)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=_callback)
    channel.start_consuming()


