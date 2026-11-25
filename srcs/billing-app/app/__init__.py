from app.config import build_database_uri, get_rabbitmq_settings
from app.models import init_db
from app.services.consumer import consume_forever


def run_billing_service() -> None:
    """Initialize database and start consuming billing messages."""
    session_factory = init_db(build_database_uri())
    rmq_settings = get_rabbitmq_settings()
    consume_forever(session_factory, rmq_settings)
