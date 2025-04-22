from flask import Blueprint, jsonify

index_router = Blueprint("index", __name__)


@index_router.route("/", methods=["GET"])
def index():
    """Index route."""
    return jsonify({"message": "Welcome to BumiBrew Market"}), 200
