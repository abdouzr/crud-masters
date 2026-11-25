import json
import signal
import time
import pika
from pika.exceptions import AMQPConnectionError, ChannelClosedByBroker
from sqlalchemy.exc import SQLAlchemyError
from app.models.order import Order


def parse_order_payload(raw_body: bytes) -> dict:
    """Parse and validate a JSON billing message body."""
    data = json.loads(raw_body.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Billing message must be a JSON object")

    missing = [key for key in ("user_id", "number_of_items", "total_amount") if key not in data]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    return {
        "user_id": int(data["user_id"]),
        "number_of_items": int(data["number_of_items"]),
        "total_amount": float(data["total_amount"]),
    }


def process_message(session_factory, raw_body: bytes) -> Order:
    """Persist a billing message into the orders table."""
    parsed = parse_order_payload(raw_body)
    with session_factory() as session:
        order = Order(**parsed)
        session.add(order)
        session.commit()
        session.refresh(order)
        return order


def consume_forever(session_factory, rmq_settings: dict) -> None:
    """Connect to RabbitMQ and consume pending and new messages from billing_queue."""
    should_stop = False
    connection = None

    def handle_signal(_signum, _frame):
        nonlocal should_stop
        should_stop = True
        if connection and connection.is_open:
            connection.add_callback_threadsafe(connection.close)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    credentials = pika.PlainCredentials(rmq_settings["user"], rmq_settings["password"])
    params = pika.ConnectionParameters(
        host=rmq_settings["host"],
        port=rmq_settings["port"],
        virtual_host=rmq_settings["vhost"],
        credentials=credentials,
        heartbeat=60,
        blocked_connection_timeout=30,
    )
    queue_name = rmq_settings["queue"]

    while not should_stop:
        try:
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue=queue_name, durable=True)
            channel.basic_qos(prefetch_count=1)

            def on_message(ch, method, _properties, body):
                try:
                    order = process_message(session_factory, body)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    print(f"Processed order id={order.id} user_id={order.user_id}", flush=True)
                except (ValueError, TypeError, json.JSONDecodeError) as err:
                    print(f"Invalid billing message rejected: {err}", flush=True)
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                except SQLAlchemyError as err:
                    print(f"Database error processing message, requeueing: {err}", flush=True)
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                    time.sleep(1)

            channel.basic_consume(queue=queue_name, on_message_callback=on_message, auto_ack=False)
            print(f"Billing consumer listening on queue '{queue_name}'...", flush=True)
            channel.start_consuming()
        except (AMQPConnectionError, ChannelClosedByBroker) as err:
            if should_stop:
                break
            print(f"RabbitMQ connection lost ({err}), retrying in 3s...", flush=True)
            time.sleep(3)
        except Exception as err:
            if should_stop:
                break
            print(f"Unexpected consumer error ({err}), retrying in 3s...", flush=True)
            time.sleep(3)
