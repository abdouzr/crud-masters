import json
import pika


def publish_billing_message(payload: dict, rmq_settings: dict) -> None:
    """Publish a JSON billing payload to the durable RabbitMQ billing_queue."""
    credentials = pika.PlainCredentials(rmq_settings["user"], rmq_settings["password"])
    params = pika.ConnectionParameters(
        host=rmq_settings["host"],
        port=rmq_settings["port"],
        virtual_host=rmq_settings["vhost"],
        credentials=credentials,
        blocked_connection_timeout=10,
    )
    connection = pika.BlockingConnection(params)
    try:
        channel = connection.channel()
        queue_name = rmq_settings["queue"]
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=pika.DeliveryMode.Persistent,
            ),
        )
    finally:
        if connection.is_open:
            connection.close()
