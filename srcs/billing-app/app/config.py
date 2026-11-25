import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")


def build_database_uri() -> str:
    """Build PostgreSQL connection URI for billing_db from environment variables."""
    if os.getenv("BILLING_DATABASE_URL"):
        return os.environ["BILLING_DATABASE_URL"]

    user = quote_plus(os.environ["BILLING_DB_USER"])
    password = quote_plus(os.environ["BILLING_DB_PASSWORD"])
    host = os.environ.get("BILLING_DB_HOST", "localhost")
    port = os.environ.get("BILLING_DB_PORT", "5432")
    db_name = os.environ.get("BILLING_DB_NAME", "billing_db")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"


def get_rabbitmq_settings() -> dict:
    """Return RabbitMQ connection settings from environment variables."""
    return {
        "host": os.environ.get("BILLING_RABBITMQ_HOST") or os.environ["RABBITMQ_HOST"],
        "port": int(os.environ.get("RABBITMQ_PORT", "5672")),
        "user": os.environ["RABBITMQ_USER"],
        "password": os.environ["RABBITMQ_PASSWORD"],
        "vhost": os.environ.get("RABBITMQ_VHOST", "/"),
        "queue": os.environ.get("RABBITMQ_QUEUE", "billing_queue"),
    }
