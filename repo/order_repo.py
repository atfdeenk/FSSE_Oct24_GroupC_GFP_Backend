from models.order import Orders
from models.order_item import OrderItems
from instance.database import db


# Order Repo
def create_order(order_data):
    order = Orders(**order_data)
    db.session.add(order)
    db.session.flush()
    return order


def get_order_by_id(order_id):
    return db.session.get(Orders, order_id)


def get_orders_by_user(user_id):
    return Orders.query.filter_by(user_id=user_id).all()


def update_order(order):
    db.session.commit()
    return order


def delete_order(order):
    for item in order.order_items:
        db.session.delete(item)
    db.session.delete(order)
    db.session.commit()


# Order Items Repo
def create_order_item(item_data):
    item = OrderItems(**item_data)
    db.session.add(item)
    return item


def get_order_items_by_order_id(order_id):
    return OrderItems.query.filter_by(order_id=order_id).all()
