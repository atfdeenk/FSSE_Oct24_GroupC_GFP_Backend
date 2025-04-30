from models.order import Orders
from models.order_item import OrderItems
from instance.database import db


# Order Repo
def create_order(order_data):
    try:
        order = Orders(**order_data)
        db.session.add(order)
        db.session.flush()  # Make order.id available
        return order
    except Exception:
        db.session.rollback()
        raise


def get_order_by_id(order_id):
    return db.session.get(Orders, order_id)


def get_orders_by_user(user_id):
    return Orders.query.filter_by(user_id=user_id).all()


def update_order(order):
    # Removed commit/rollback to delegate transaction management to service layer
    return order


def delete_order(order):
    # Removed commit/rollback to delegate transaction management to service layer
    db.session.delete(order)


# Order Items Repo
def create_order_item(item_data):
    try:
        item = OrderItems(**item_data)
        db.session.add(item)
        return item
    except Exception:
        db.session.rollback()
        raise


def get_order_items_by_order_id(order_id):
    return OrderItems.query.filter_by(order_id=order_id).all()
