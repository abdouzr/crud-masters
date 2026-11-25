from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


def init_db(database_uri: str):
    """Create SQLAlchemy engine, initialize tables, and return sessionmaker."""
    engine = create_engine(database_uri, pool_pre_ping=True)
    # Import models before create_all so metadata includes all tables
    from app.models.order import Order  # noqa: F401
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
