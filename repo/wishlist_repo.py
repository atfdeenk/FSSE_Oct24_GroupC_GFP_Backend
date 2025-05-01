from instance.database import db
from models.wishlist_item import WishlistItems


def get_user_wishlist(user_id: int):
    return (
        WishlistItems.query.filter_by(user_id=user_id).join(WishlistItems.vendor).all()
    )


def add_to_wishlist(user_id: int, product_id: int, vendor_id: int):
    wishlist_item = WishlistItems(
        user_id=user_id, product_id=product_id, vendor_id=vendor_id
    )
    db.session.add(wishlist_item)
    return wishlist_item


def remove_from_wishlist(user_id: int, product_id: int):
    wishlist_item = WishlistItems.query.filter_by(
        user_id=user_id, product_id=product_id
    ).first()
    if wishlist_item:
        db.session.delete(wishlist_item)
    return wishlist_item


def clear_wishlist(user_id: int):
    WishlistItems.query.filter_by(user_id=user_id).delete()
