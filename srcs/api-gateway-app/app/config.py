import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")


def get_inventory_url() -> str:
    """Return the base URL of the Inventory API."""
    return os.environ["INVENTORY_API_URL"].rstrip("/")


def get_rabbitmq_settings() -> dict:
    """Return RabbitMQ connection settings from environment variables."""
    return {
        "host": os.environ["RABBITMQ_HOST"],
        "port": int(os.environ.get("RABBITMQ_PORT", "5672")),
        "user": os.environ["RABBITMQ_USER"],
        "password": os.environ["RABBITMQ_PASSWORD"],
        "vhost": os.environ.get("RABBITMQ_VHOST", "/"),
        "queue": os.environ.get("RABBITMQ_QUEUE", "billing_queue"),
    }
