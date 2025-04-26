from models.product import Products
from repo import order_repo
from sqlalchemy.exc import IntegrityError
from instance.database import db


def create_order_with_items(user_id, items):
    """Create an order and its items."""
    total_amount = sum(item["quantity"] * item["unit_price"] for item in items)

    # Create the order first
    order_data = {"user_id": user_id, "total_amount": total_amount, "status": "pending"}
    try:
        order = order_repo.create_order(order_data)

        # For each item, get the vendor_id from the product
        for item in items:
            product = Products.query.get(item["product_id"])  # Fetch the product
            if not product:
                return None, f"Product with id {item['product_id']} not found."

            item_data = {
                "order_id": order.id,
                "product_id": item["product_id"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
                "vendor_id": product.vendor_id,  # Get vendor_id from product
            }
            order_repo.create_order_item(item_data)

        db.session.commit()
        return order, None
    except IntegrityError as e:
        db.session.rollback()  # Rollback if error occurs
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

    # Delete order items
    for item in order.order_items:
        db.session.delete(item)

    # Delete order
    db.session.delete(order)
    db.session.commit()

    return order, None
