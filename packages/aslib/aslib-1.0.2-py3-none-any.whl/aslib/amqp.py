from typing import Tuple, Optional

import pika

from .options import MQOption


def Publish(target: MQOption, raw: bytes) -> Tuple[bool, Optional[Exception]]:
    try:
        with pika.BlockingConnection(
                parameters=pika.ConnectionParameters(
                    host=target.host,
                    port=target.port,
                    virtual_host=target.namespace,
                    credentials=pika.PlainCredentials(username=target.user, password=target.password),
                )
        ) as connection:
            with connection.channel() as channel:
                channel.exchange_declare(exchange=target.exchange, exchange_type=target.exchange_type, durable=True)
                channel.queue_declare(queue=target.queue, durable=True)
                channel.queue_bind(exchange=target.exchange, queue=target.queue, routing_key=target.routing_key)
                channel.confirm_delivery()
                channel.basic_publish(
                    exchange=target.exchange,
                    routing_key=target.routing_key,
                    body=raw,
                    properties=pika.BasicProperties(delivery_mode=2),
                    mandatory=True,
                )
                return True, None
    except Exception as err:
        return False, err
