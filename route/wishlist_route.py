from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import wishlist_services

wishlist_bp = Blueprint("wishlist", __name__, url_prefix="/wishlist")


@wishlist_bp.route("/", methods=["GET"])
@jwt_required()
def get_wishlist():
    user_id = get_jwt_identity()
    wishlist = wishlist_services.get_user_wishlist(user_id)
    return (
        jsonify(
            [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "vendor_id": item.vendor_id,
                    "added_at": item.added_at.isoformat(),
                }
                for item in wishlist
            ]
        ),
        200,
    )


@wishlist_bp.route("/add", methods=["POST"])
@jwt_required()
def add_to_wishlist():
    user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data.get("product_id")
    vendor_id = data.get("vendor_id")
    if not product_id or not vendor_id:
        return jsonify({"error": "Missing product_id or vendor_id"}), 400
    item = wishlist_services.add_to_wishlist(user_id, product_id, vendor_id)
    return jsonify({"message": "Item added to wishlist", "id": item.id}), 201


@wishlist_bp.route("/remove", methods=["DELETE"])
@jwt_required()
def remove_from_wishlist():
    user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data.get("product_id")
    if not product_id:
        return jsonify({"error": "Missing product_id"}), 400
    wishlist_services.remove_from_wishlist(user_id, product_id)
    return jsonify({"message": "Item removed from wishlist"}), 200


@wishlist_bp.route("/clear", methods=["DELETE"])
@jwt_required()
def clear_wishlist():
    user_id = get_jwt_identity()
    wishlist_services.clear_wishlist(user_id)
    return jsonify({"message": "Wishlist cleared"}), 200
