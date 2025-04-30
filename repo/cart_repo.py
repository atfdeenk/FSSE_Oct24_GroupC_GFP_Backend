from models.cart import Cart
from instance.database import db


def get_cart_by_user(user_id):
    return Cart.query.filter_by(user_id=user_id).first()


def create_cart_for_user(user_id):
    cart = Cart(user_id=user_id)
    db.session.add(cart)
    db.session.flush()  # Assign id before returning
    return cart
