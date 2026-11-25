from app.models import db


class Movie(db.Model):
    """SQLAlchemy model representing a movie in the movies table."""

    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def to_dict(self) -> dict:
        """Serialize Movie instance to a JSON-compatible dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
        }
