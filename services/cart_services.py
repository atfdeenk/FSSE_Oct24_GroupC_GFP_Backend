from repo import cart_repo, cart_item_repo
from instance.database import db


def get_or_create_cart(user_id):
    cart = cart_repo.get_cart_by_user(user_id)
    if not cart:
        try:
            cart = cart_repo.create_cart_for_user(user_id)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
    return cart


def add_item_to_cart(user_id, product_id, quantity):
    cart = get_or_create_cart(user_id)
    try:
        item = cart_item_repo.add_cart_item(cart.id, product_id, quantity)
        db.session.commit()
        return item
    except Exception:
        db.session.rollback()
        raise
