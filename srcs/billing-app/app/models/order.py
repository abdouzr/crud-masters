from sqlalchemy import Column, Float, Integer
from app.models import Base


class Order(Base):
    """SQLAlchemy model representing a billing order in the orders table."""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    number_of_items = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)
