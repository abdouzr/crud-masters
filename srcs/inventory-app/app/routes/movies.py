from flask import Blueprint, jsonify, request
from app.models import db
from app.models.movie import Movie

movies_bp = Blueprint("movies", __name__, url_prefix="/api/movies")


@movies_bp.route("", methods=["GET"], strict_slashes=False)
def get_movies():
    """Retrieve all movies or filter movies by title substring."""
    title = request.args.get("title")
    query = Movie.query
    if title:
        query = query.filter(Movie.title.ilike(f"%{title}%"))
    movies = query.order_by(Movie.id.asc()).all()
    return jsonify([movie.to_dict() for movie in movies]), 200


@movies_bp.route("", methods=["POST"], strict_slashes=False)
def create_movie():
    """Create a new movie entry in the inventory."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"message": "Invalid JSON payload"}), 400

    title = data.get("title")
    description = data.get("description")
    if not isinstance(title, str) or not title.strip() or not isinstance(description, str):
        return jsonify({"message": "Both 'title' and 'description' are required"}), 400

    movie = Movie(title=title.strip(), description=description)
    db.session.add(movie)
    db.session.commit()
    return jsonify(movie.to_dict()), 201


@movies_bp.route("", methods=["DELETE"], strict_slashes=False)
def delete_all_movies():
    """Delete all movies from the database."""
    Movie.query.delete()
    db.session.commit()
    return jsonify({"message": "All movies deleted"}), 200


@movies_bp.route("/<int:movie_id>", methods=["GET"], strict_slashes=False)
def get_movie(movie_id: int):
    """Retrieve a single movie by its ID."""
    movie = db.session.get(Movie, movie_id)
    if movie is None:
        return jsonify({"message": "Movie not found"}), 404
    return jsonify(movie.to_dict()), 200


@movies_bp.route("/<int:movie_id>", methods=["PUT"], strict_slashes=False)
def update_movie(movie_id: int):
    """Update a single movie by its ID."""
    movie = db.session.get(Movie, movie_id)
    if movie is None:
        return jsonify({"message": "Movie not found"}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or ("title" not in data and "description" not in data):
        return jsonify({"message": "Provide 'title' and/or 'description' to update"}), 400

    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return jsonify({"message": "'title' must be a non-empty string"}), 400
        movie.title = data["title"].strip()

    if "description" in data:
        if not isinstance(data["description"], str):
            return jsonify({"message": "'description' must be a string"}), 400
        movie.description = data["description"]

    db.session.commit()
    return jsonify(movie.to_dict()), 200


@movies_bp.route("/<int:movie_id>", methods=["DELETE"], strict_slashes=False)
def delete_movie(movie_id: int):
    """Delete a single movie by its ID."""
    movie = db.session.get(Movie, movie_id)
    if movie is None:
        return jsonify({"message": "Movie not found"}), 404

    db.session.delete(movie)
    db.session.commit()
    return jsonify({"message": "Movie deleted"}), 200
