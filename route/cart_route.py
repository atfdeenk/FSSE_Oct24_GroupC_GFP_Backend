from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services import cart_services as cart_service
from services import cart_item_services as cart_item_service
from shared.auth import role_required

cart_bp = Blueprint("cart_bp", __name__)

@cart_bp.route("/cart", methods=["GET"])
@jwt_required()
@role_required("customer")
def get_cart():
    user_id = int(get_jwt_identity())
    current_app.logger.info(f"User {user_id} requested their cart.")
    cart = cart_service.get_or_create_cart(user_id)
    return jsonify({
        "message": "Cart retrieved successfully.",
        "cart_id": cart.id,
        "user_id": cart.user_id,
    }), 200

@cart_bp.route("/cart/items", methods=["POST"])
@jwt_required()
@role_required("customer")
def add_item():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)
    current_app.logger.info(f"User {user_id} adding product {product_id} (qty {quantity}) to cart.")

    item = cart_service.add_item_to_cart(user_id, product_id, quantity)
    return jsonify({
        "message": "Item added to cart successfully.",
        "cart_id": item.cart_id,
        "product_id": item.product_id,
        "quantity": item.quantity
    }), 201

@cart_bp.route("/cart/items", methods=["GET"])
@jwt_required()
@role_required("customer")
def get_cart_items():
    user_id = int(get_jwt_identity())
    current_app.logger.info(f"User {user_id} requested their cart items.")
    items = cart_item_service.get_cart_items(user_id)
    return jsonify({
        "message": "Cart items fetched successfully.",
        "items": [
            {
                "id": i.id,
                "product_id": i.product_id,
                "quantity": i.quantity
            } for i in items
        ]
    }), 200

@cart_bp.route("/cart/items/<int:item_id>", methods=["PATCH"])
@jwt_required()
@role_required("customer")
def update_item(item_id):
    user_id = int(get_jwt_identity())
    role = get_jwt().get("role")
    data = request.get_json()
    quantity = data.get("quantity")
    current_app.logger.info(f"User {user_id} updating cart item {item_id} to quantity {quantity}.")
    updated = cart_item_service.update_item(item_id, quantity)
    if not updated:
        current_app.logger.warning(f"User {user_id} tried to update non-existent cart item {item_id}.")
        return jsonify({"message": "Cart item not found."}), 404
    return jsonify({
        "message": "Cart item updated successfully.",
        "id": updated.id,
        "quantity": updated.quantity
    }), 200

@cart_bp.route("/cart/items/<int:item_id>", methods=["DELETE"])
@jwt_required()
@role_required("customer")
def delete_item(item_id):
    user_id = int(get_jwt_identity())
    role = get_jwt().get("role")
    current_app.logger.info(f"User {user_id} deleting cart item {item_id}.")
    success = cart_item_service.delete_item(item_id)
    if not success:
        current_app.logger.warning(f"User {user_id} tried to delete non-existent cart item {item_id}.")
        return jsonify({"message": "Cart item not found."}), 404
    return jsonify({"message": "Item removed from cart successfully."}), 200
