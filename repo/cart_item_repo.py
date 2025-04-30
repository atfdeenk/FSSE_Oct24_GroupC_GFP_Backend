from models.cart_item import CartItems
from instance.database import db


def add_cart_item(cart_id, product_id, quantity):
    existing = CartItems.query.filter_by(cart_id=cart_id, product_id=product_id).first()
    if existing:
        existing.quantity += quantity
        return existing

    item = CartItems(cart_id=cart_id, product_id=product_id, quantity=quantity)
    db.session.add(item)
    return item


def get_cart_items(cart_id):
    return CartItems.query.filter_by(cart_id=cart_id).all()


def get_cart_item_by_id(cart_item_id):
    item = db.session.get(CartItems, cart_item_id)
    return item


def update_cart_item_quantity(cart_item_id, quantity):
    item = db.session.get(CartItems, cart_item_id)
    if item:
        item.quantity = quantity
    return item


def remove_cart_item(cart_item_id):
    item = db.session.get(CartItems, cart_item_id)
    if item:
        db.session.delete(item)
        return True
    return False
