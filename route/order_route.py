from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import order_services

order_bp = Blueprint("order_bp", __name__)


# Create an order with items
@order_bp.route("/orders", methods=["POST"])
@jwt_required()
def create_order():
    data = request.get_json()
    items = data.get("items", [])
    vendor_id = data.get("vendor_id")
    current_user = get_jwt_identity()

    if not items:
        return jsonify({"msg": "No items to order"}), 400

    if not vendor_id:
        return jsonify({"msg": "Vendor ID is required"}), 400

    # Validate each item has required keys
    required_keys = {"product_id", "quantity", "unit_price"}
    for idx, item in enumerate(items):
        if not all(key in item for key in required_keys):
            return (
                jsonify(
                    {
                        "msg": f"Item at index {idx} is missing required keys: {required_keys}"
                    }
                ),
                400,
            )

    order, error = order_services.create_order_with_items(current_user, items)
    if error:
        return jsonify({"msg": error}), 400

    return jsonify({"msg": "Order created", "order_id": order.id}), 201


# Get a specific order
@order_bp.route("/orders/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    order = order_services.get_order(order_id)
    if not order:
        return jsonify({"msg": "Order not found"}), 404

    items = order_services.get_order_items(order_id)
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
                            "quantity": item.quantity,
                            "unit_price": float(item.unit_price),
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
    orders = order_services.get_user_orders(current_user)

    return (
        jsonify(
            [
                {
                    "id": order.id,
                    "total_amount": str(order.total_amount),
                    "status": order.status,
                    "created_at": order.created_at.isoformat(),
                }
                for order in orders
            ]
        ),
        200,
    )


# Update order status
@order_bp.route("/orders/<int:order_id>/status", methods=["PUT"])
@jwt_required()
def update_order_status(order_id):
    data = request.get_json()
    status = data.get("status")

    if not status:
        return jsonify({"msg": "Status is required"}), 400

    order, error = order_services.update_order_status(order_id, status)
    if error:
        return jsonify({"msg": error}), 404

    return jsonify({"msg": "Order status updated"}), 200


# Delete an order
@order_bp.route("/orders/<int:order_id>", methods=["DELETE"])
@jwt_required()
def delete_order(order_id):
    order, error = order_services.delete_order(order_id)
    if error:
        return jsonify({"msg": error}), 404

    return jsonify({"msg": "Order deleted"}), 200
