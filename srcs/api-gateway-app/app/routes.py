from flask import Blueprint, Response, jsonify, request
import requests
from app.config import get_inventory_url, get_rabbitmq_settings
from app.rabbitmq import publish_billing_message

gateway_bp = Blueprint("gateway", __name__)

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "content-length",
    "content-encoding",
    "host",
}


def _forward_to_inventory(target_path: str) -> Response:
    """Proxy an incoming request to the Inventory API and return its exact response."""
    base_url = get_inventory_url()
    target_url = f"{base_url}{target_path}"
    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }

    try:
        upstream_resp = requests.request(
            method=request.method,
            url=target_url,
            params=request.args,
            data=request.get_data(),
            headers=headers,
            timeout=10,
        )
    except requests.RequestException as err:
        return jsonify({"message": f"Inventory service unavailable: {err}"}), 502

    response_headers = [
        (key, value)
        for key, value in upstream_resp.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    ]
    return Response(upstream_resp.content, status=upstream_resp.status_code, headers=response_headers)


@gateway_bp.route("/api/movies", methods=["GET", "POST", "DELETE"], strict_slashes=False)
def proxy_movies_collection():
    """Forward collection requests for /api/movies to Inventory API."""
    return _forward_to_inventory("/api/movies")


@gateway_bp.route("/api/movies/<path:subpath>", methods=["GET", "PUT", "DELETE"], strict_slashes=False)
def proxy_movies_item(subpath: str):
    """Forward single-resource requests for /api/movies/<id> to Inventory API."""
    return _forward_to_inventory(f"/api/movies/{subpath}")


@gateway_bp.route("/api/billing", methods=["POST"], strict_slashes=False)
def queue_billing():
    """Publish a billing request payload to RabbitMQ billing_queue."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"message": "Invalid JSON payload"}), 400

    try:
        publish_billing_message(payload, get_rabbitmq_settings())
    except Exception as err:
        return jsonify({"message": f"Failed to queue message: {err}"}), 500

    return jsonify({"message": "Message posted"}), 200
