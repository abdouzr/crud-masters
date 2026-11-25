from flask import Flask, jsonify
from app.models import db
from app.routes.movies import movies_bp


def create_app(config_overrides: dict | None = None) -> Flask:
    """Create and configure the Inventory Flask application."""
    app = Flask(__name__)

    if config_overrides:
        app.config.update(config_overrides)
    else:
        from app.config import Config
        app.config.from_object(Config)

    db.init_app(app)
    app.register_blueprint(movies_bp)

    @app.route("/", methods=["GET"])
    def health():
        return jsonify({"message": "Inventory API is running"}), 200

    with app.app_context():
        db.create_all()

    return app
