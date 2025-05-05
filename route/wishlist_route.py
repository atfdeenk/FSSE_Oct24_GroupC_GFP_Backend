from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import wishlist_services

wishlist_bp = Blueprint("wishlist", __name__, url_prefix="/wishlist")


@wishlist_bp.route("/", methods=["GET"])
@jwt_required()
def get_wishlist():
    user_id = get_jwt_identity()
    current_app.logger.info("GET /wishlist/ called by user: %s", user_id)
    wishlist = wishlist_services.get_user_wishlist(user_id)
    if not wishlist:
        return jsonify({"message": "Wishlist is empty", "wishlist": []}), 200
    return (
        jsonify(
            {
                "message": f"Wishlist contains {len(wishlist)} items",
                "wishlist": [
                    {
                        "id": item.id,
                        "product_id": item.product_id,
                        "vendor_id": item.vendor_id,
                        "vendor_username": (
                            item.vendor.username if item.vendor else None
                        ),
                        "added_at": item.added_at.isoformat(),
                    }
                    for item in wishlist
                ],
            }
        ),
        200,
    )


@wishlist_bp.route("/add", methods=["POST"])
@jwt_required()
def add_to_wishlist():
    user_id = get_jwt_identity()
    current_app.logger.info("POST /wishlist/add called by user: %s", user_id)
    data = request.get_json()
    product_id = data.get("product_id")
    vendor_id = data.get("vendor_id")

    if not product_id or not vendor_id:
        return jsonify({"message": "Missing product_id or vendor_id"}), 400

    item = wishlist_services.add_to_wishlist(user_id, product_id, vendor_id)

    if item is None:
        return jsonify({"message": "Item already exists in wishlist"}), 200

    return jsonify({"message": "Item added to wishlist", "id": item.id}), 201


@wishlist_bp.route("/remove", methods=["DELETE"])
@jwt_required()
def remove_from_wishlist():
    user_id = get_jwt_identity()
    current_app.logger.info("DELETE /wishlist/remove called by user: %s", user_id)
    data = request.get_json()
    product_id = data.get("product_id")
    if not product_id:
        return jsonify({"message": "Missing product_id"}), 400
    # Check if item exists before removal
    wishlist = wishlist_services.get_user_wishlist(user_id)
    item_exists = any(item.product_id == product_id for item in wishlist)
    if not item_exists:
        current_app.logger.warning("Attempt to remove non-existent wishlist item: user=%s, product_id=%s", user_id, product_id)
        return jsonify({"message": "Item not found in wishlist"}), 404
    wishlist_services.remove_from_wishlist(user_id, product_id)
    current_app.logger.info("Wishlist item removed: user=%s, product_id=%s", user_id, product_id)
    return jsonify({"message": "Item removed from wishlist"}), 200


@wishlist_bp.route("/clear", methods=["DELETE"])
@jwt_required()
def clear_wishlist():
    user_id = get_jwt_identity()
    current_app.logger.info("DELETE /wishlist/clear called by user: %s", user_id)
    wishlist = wishlist_services.get_user_wishlist(user_id)
    if not wishlist:
        current_app.logger.warning("Attempt to clear already empty wishlist: user=%s", user_id)
    wishlist_services.clear_wishlist(user_id)
    return jsonify({"message": "Wishlist cleared"}), 200
