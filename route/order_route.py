from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import order_services

order_bp = Blueprint("order_bp", __name__)


# Create an order with items
@order_bp.route("/orders", methods=["POST"])
@jwt_required()
def create_order():
    data = request.get_json()
    items = data.get("items", [])
    current_user = get_jwt_identity()

    current_app.logger.info(f"User {current_user} is attempting to create an order.")

    if not items:
        current_app.logger.warning("Order creation failed: No items provided.")
        return jsonify({"msg": "No items to order"}), 400

    required_keys = {"product_id", "quantity", "unit_price"}
    for idx, item in enumerate(items):
        if not all(key in item for key in required_keys):
            current_app.logger.warning(
                f"Order creation failed: Item at index {idx} missing keys."
            )
            return (
                jsonify(
                    {
                        "msg": f"Item at index {idx} is missing required keys: {required_keys}"
                    }
                ),
                400,
            )

    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user

    order, error = order_services.create_order_with_items(user_id, items)
    if error:
        current_app.logger.error(f"Order creation failed: {error}")
        return jsonify({"msg": error}), 400

    order_items = order_services.get_order_items(order.id)

    response_items = [
        {
            "product_id": item.product_id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "image_url": item.product.image_url,
            "unit_price": float(item.unit_price),
            "vendor_id": item.product.vendor_id,
        }
        for item in order_items
    ]

    current_app.logger.info(f"Order {order.id} created successfully by user {user_id}.")

    return (
        jsonify(
            {
                "msg": "Order created",
                "order_id": order.id,
                "items": response_items,
            }
        ),
        201,
    )


# Get a specific order
@order_bp.route("/orders/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    current_app.logger.info(f"Fetching order {order_id}.")
    order = order_services.get_order(order_id)
    if not order:
        current_app.logger.warning(f"Order {order_id} not found.")
        return jsonify({"msg": "Order not found"}), 404

    items = order_services.get_order_items(order_id)
    current_app.logger.info(f"Order {order_id} fetched successfully.")
    return (
        jsonify(
            {
                "order": {
                    "id": order.id,
                    "total_amount": str(order.total_amount),
                    "status": order.status,
                    "created_at": order.created_at.isoformat(),
                    "items": [
                        {
                            "product_id": item.product_id,
                            "product_name": item.product.name,
                            "quantity": item.quantity,
                            "image_url": item.product.image_url,
                            "unit_price": float(item.unit_price),
                            "vendor_id": item.product.vendor_id,
                            "vendor_name": (
                                item.product.vendor.username
                                if item.product.vendor
                                else None
                            ),
                        }
                        for item in items
                    ],
                }
            }
        ),
        200,
    )


# Get all orders of the current user
@order_bp.route("/orders", methods=["GET"])
@jwt_required()
def get_user_orders():
    current_user = get_jwt_identity()
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user
    current_app.logger.info(f"Fetching all orders for user {user_id}.")
    orders = order_services.get_user_orders(user_id)

    orders_with_items = []
    for order in orders:
        order_items = order_services.get_order_items(order.id)
        items = [
            {
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "image_url": item.product.image_url,
                "unit_price": float(item.unit_price),
                "vendor_id": item.product.vendor_id,
                "vendor_name": (
                    item.product.vendor.username if item.product.vendor else None
                ),
            }
            for item in order_items
        ]
        orders_with_items.append(
            {
                "id": order.id,
                "total_amount": str(order.total_amount),
                "status": order.status,
                "created_at": order.created_at.isoformat(),
                "items": items,
            }
        )

    current_app.logger.info(f"Fetched {len(orders_with_items)} orders for user {user_id}.")

    return (
        jsonify(orders_with_items),
        200,
    )


# Update order status
@order_bp.route("/orders/<int:order_id>/status", methods=["PUT"])
@jwt_required()
def update_order_status(order_id):
    data = request.get_json()
    status = data.get("status")

    if not status:
        current_app.logger.warning(f"Order status update failed: No status provided for order {order_id}.")
        return jsonify({"msg": "Status is required"}), 400

    order, error = order_services.update_order_status(order_id, status)
    if error:
        if error == "Order not found.":
            current_app.logger.warning(f"Order status update failed: {error} (order {order_id})")
            return jsonify({"msg": error}), 404
        current_app.logger.error(f"Order status update failed: {error} (order {order_id})")
        return jsonify({"msg": error}), 400

    current_app.logger.info(f"Order {order_id} status updated to {status}.")
    return jsonify({"msg": "Order status updated"}), 200


# Delete an order
@order_bp.route("/orders/<int:order_id>", methods=["DELETE"])
@jwt_required()
def delete_order(order_id):
    order, error = order_services.delete_order(order_id)
    if error:
        current_app.logger.warning(f"Order deletion failed: {error} (order {order_id})")
        return jsonify({"msg": error}), 404

    current_app.logger.info(f"Order {order_id} deleted successfully.")
    return jsonify({"msg": "Order deleted"}), 200
