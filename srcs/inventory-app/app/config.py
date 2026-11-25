import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")


def build_database_uri() -> str:
    """Build PostgreSQL connection URI from environment variables."""
    if os.getenv("INVENTORY_DATABASE_URL"):
        return os.environ["INVENTORY_DATABASE_URL"]

    user = quote_plus(os.environ["INVENTORY_DB_USER"])
    password = quote_plus(os.environ["INVENTORY_DB_PASSWORD"])
    host = os.environ.get("INVENTORY_DB_HOST", "localhost")
    port = os.environ.get("INVENTORY_DB_PORT", "5432")
    db_name = os.environ.get("INVENTORY_DB_NAME", "movies_db")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"


class Config:
    """Flask application configuration for the Inventory API."""

    SQLALCHEMY_DATABASE_URI = build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
