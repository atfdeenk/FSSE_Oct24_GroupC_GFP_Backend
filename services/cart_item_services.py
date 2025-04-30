from repo import cart_repo, cart_item_repo
from instance.database import db


def get_cart_items(user_id):
    cart = cart_repo.get_cart_by_user(user_id)
    return cart_item_repo.get_cart_items(cart.id) if cart else []


def add_item(user_id, product_id, quantity):
    cart = cart_repo.get_cart_by_user(user_id)
    if not cart:
        cart = cart_repo.create_cart_for_user(user_id)
    try:
        item = cart_item_repo.add_cart_item(cart.id, product_id, quantity)
        db.session.commit()
        return item
    except Exception:
        db.session.rollback()
        raise


def update_item(cart_item_id, quantity):
    try:
        item = cart_item_repo.update_cart_item_quantity(cart_item_id, quantity)
        db.session.commit()
        return item
    except Exception:
        db.session.rollback()
        raise


def delete_item(cart_item_id):
    try:
        result = cart_item_repo.remove_cart_item(cart_item_id)
        db.session.commit()
        return result
    except Exception:
        db.session.rollback()
        raise
