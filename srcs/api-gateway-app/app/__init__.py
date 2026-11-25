from flask import Flask, jsonify
from app.routes import gateway_bp


def create_app() -> Flask:
    """Create and configure the API Gateway Flask application."""
    app = Flask(__name__)
    app.register_blueprint(gateway_bp)

    @app.route("/", methods=["GET"])
    def health():
        return jsonify({"message": "API Gateway is running"}), 200

    return app
