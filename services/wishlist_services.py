from repo import wishlist_repo
from models.wishlist_item import WishlistItems
from instance.database import db
from sqlalchemy.exc import SQLAlchemyError
import logging


def get_user_wishlist(user_id: int):
    return wishlist_repo.get_user_wishlist(user_id)


def add_to_wishlist(user_id: int, product_id: int, vendor_id: int):
    # Check if the item already exists
    existing_item = WishlistItems.query.filter_by(
        user_id=user_id, product_id=product_id
    ).first()

    if existing_item:
        # Already in wishlist, do not add again
        return None

    # Otherwise, create a new wishlist item
    item = WishlistItems(user_id=user_id, product_id=product_id, vendor_id=vendor_id)
    db.session.add(item)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error committing add_to_wishlist: {e}")
        raise
    return item


def remove_from_wishlist(user_id: int, product_id: int):
    try:
        result = wishlist_repo.remove_from_wishlist(user_id, product_id)
        db.session.commit()
        return result
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error committing remove_from_wishlist: {e}")
        raise


def clear_wishlist(user_id: int):
    try:
        result = wishlist_repo.clear_wishlist(user_id)
        db.session.commit()
        return result
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Error committing clear_wishlist: {e}")
        raise
