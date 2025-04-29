from models.product import Products
from repo import order_repo
from sqlalchemy.exc import IntegrityError
from instance.database import db


# Define allowed transitions
ALLOWED_STATUS_TRANSITIONS = {
    "pending": ["shipped", "cancelled"],
    "shipped": ["delivered", "cancelled"],
    "delivered": ["completed"],
    "completed": [],
    "cancelled": [],
}


def create_order_with_items(user_id, items):
    """Create an order and its items transactionally."""
    total_amount = sum(item["quantity"] * item["unit_price"] for item in items)

    try:
        with db.session.begin_nested():  # 🚀 Start nested transaction
            order_data = {
                "user_id": user_id,
                "total_amount": total_amount,
                "status": "pending",
            }
            order = order_repo.create_order(order_data)

            for item in items:
                product = db.session.get(Products, item["product_id"])
                if not product:
                    raise ValueError(f"Product with id {item['product_id']} not found.")

                if product.stock_quantity <= 0:
                    raise ValueError(f"Product {product.name} is out of stock.")

                if item["quantity"] > product.stock_quantity:
                    raise ValueError(
                        f"Requested quantity for {product.name} exceeds stock."
                    )

                order_repo.create_order_item(
                    {
                        "order_id": order.id,
                        "product_id": item["product_id"],
                        "quantity": item["quantity"],
                        "unit_price": item["unit_price"],
                        "vendor_id": product.vendor_id,
                    }
                )

        return order, None

    except (IntegrityError, ValueError) as e:
        db.session.rollback()
        return None, str(e)


def get_order(order_id):
    return order_repo.get_order_by_id(order_id)


def get_user_orders(user_id):
    return order_repo.get_orders_by_user(user_id)


def get_order_items(order_id):
    return order_repo.get_order_items_by_order_id(order_id)


def update_order_status(order_id, new_status):
    from models.order import Orders

    try:
        new_status = new_status.lower()  # normalize input
        if new_status not in ALLOWED_STATUS_TRANSITIONS:
            return (
                None,
                f"Invalid status '{new_status}'. Allowed statuses are {list(ALLOWED_STATUS_TRANSITIONS.keys())}.",
            )

        with db.session.begin_nested():
            order = db.session.get(Orders, order_id)
            if not order:
                return None, "Order not found."

            current_status = order.status.lower()

            # Prevent updating completed or cancelled orders
            if current_status in ["completed", "cancelled"]:
                return (
                    None,
                    f"Cannot change status from '{current_status}'. The order is already closed.",
                )

            # Check if transition is allowed
            allowed_next_statuses = ALLOWED_STATUS_TRANSITIONS.get(current_status, [])
            if new_status not in allowed_next_statuses:
                return (
                    None,
                    f"Cannot change status from '{current_status}' to '{new_status}'. Allowed transitions: {allowed_next_statuses}",
                )

            # If moving to 'completed', decrease product stock
            if new_status == "completed":
                for item in order.order_items:
                    product = db.session.get(Products, item.product_id)
                    if not product:
                        raise ValueError(
                            f"Product with ID {item.product_id} not found."
                        )

                    if product.stock_quantity < item.quantity:
                        raise ValueError(
                            f"Not enough stock for product {product.name}."
                        )

                    product.stock_quantity -= item.quantity

            # Update order status
            order.status = new_status

        return order, None

    except (IntegrityError, ValueError) as e:
        db.session.rollback()
        return None, str(e)
    except Exception as e:
        db.session.rollback()
        return None, str(e)


def delete_order(order_id):
    order = order_repo.get_order_by_id(order_id)
    if not order:
        return None, "Order not found"

    order_repo.delete_order(order)
    return order, None
