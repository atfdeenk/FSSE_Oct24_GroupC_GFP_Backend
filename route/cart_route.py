from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services import cart_services as cart_service
from services import cart_item_services as cart_item_service
from shared.auth import role_required
from decimal import Decimal


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


@cart_bp.route("/cart/summary", methods=["GET"])
@jwt_required()
@role_required("customer")
def get_cart_summary():
    from models.voucher import Vouchers
    from datetime import datetime

    user_id = int(get_jwt_identity())
    voucher_code = request.args.get("voucher_code")

    # 1. Get cart items
    items = cart_item_service.get_cart_items(user_id)
    if not items:
        return jsonify({"msg": "Cart is empty"}), 400

    # 2. Total before discount
    total_before = sum(i.quantity * i.product.price for i in items)
    discount = 0
    voucher = None

    if voucher_code:
        voucher = Vouchers.query.filter_by(code=voucher_code, is_active=True).first()
        if not voucher or (voucher.expires_at and voucher.expires_at < datetime.utcnow()):
            return jsonify({"msg": "Voucher is invalid or expired"}), 400

        # 🔒 Enforce voucher only applies if all products are from the voucher's vendor
        distinct_vendor_ids = {i.product.vendor_id for i in items}
        if len(distinct_vendor_ids) != 1 or voucher.vendor_id not in distinct_vendor_ids:
            return jsonify({"msg": "Voucher can only be used for products from the issuing vendor"}), 400

        # Calculate discount
        if voucher.discount_percent:
            discount = total_before * (Decimal(str(voucher.discount_percent)) / Decimal("100"))
        elif voucher.discount_amount:
            discount = Decimal(str(voucher.discount_amount))

    total_after = max(total_before - discount, Decimal("0"))

    return jsonify({
        "total_before_discount": float(total_before),
        "discount_amount": float(discount),
        "total_after_discount": float(total_after),
        "voucher_code": voucher.code if voucher else None,
        "items": [
            {
                "product_id": i.product_id,
                "product_name": i.product.name,
                "unit_price": float(i.product.price),
                "quantity": i.quantity,
                "vendor_id": i.product.vendor_id,
                "vendor_name": i.product.vendor.username if i.product.vendor else None
            } for i in items
        ]
    }), 200
