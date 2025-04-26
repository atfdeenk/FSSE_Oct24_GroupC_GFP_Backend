from repo import order_repo
from sqlalchemy.exc import IntegrityError


def create_order_with_items(user_id, items):
    """Create an order and its items."""
    total_amount = sum(item["quantity"] * item["unit_price"] for item in items)
    order_data = {"user_id": user_id, "total_amount": total_amount, "status": "pending"}
    try:
        order = order_repo.create_order(order_data)

        for item in items:
            item_data = {
                "order_id": order.id,
                "product_id": item["product_id"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
            }
            order_repo.create_order_item(item_data)

        return order, None
    except IntegrityError as e:
        return None, str(e)


def get_order(order_id):
    return order_repo.get_order_by_id(order_id)


def get_user_orders(user_id):
    return order_repo.get_orders_by_user(user_id)


def get_order_items(order_id):
    return order_repo.get_order_items_by_order_id(order_id)


def update_order_status(order_id, status):
    order = order_repo.get_order_by_id(order_id)
    if not order:
        return None, "Order not found"

    order.status = status
    order_repo.update_order(order)
    return order, None


def delete_order(order_id):
    order = order_repo.get_order_by_id(order_id)
    if not order:
        return None, "Order not found"

    order_repo.delete_order(order)
    return order, None
