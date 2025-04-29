import pytest
from flask import Flask
from instance.database import db
from models.wishlist_item import WishlistItems
from models.user import Users
from models.product import Product
from services import wishlist_services


def test_add_to_wishlist(app, client, new_user, seed_product):
    item = wishlist_services.add_to_wishlist(
        user_id=new_user.id,
        product_id=seed_product.id,
        vendor_id=new_user.id,  # Assuming same user is vendor for test
    )
    assert item is not None
    assert item.user_id == new_user.id
    assert item.product_id == seed_product.id


def test_get_user_wishlist(app, client, new_user, seed_product):
    wishlist_services.add_to_wishlist(
        user_id=new_user.id, product_id=seed_product.id, vendor_id=new_user.id
    )
    wishlist = wishlist_services.get_user_wishlist(new_user.id)
    assert len(wishlist) == 1
    assert wishlist[0].product_id == seed_product.id


def test_remove_from_wishlist(app, client, new_user, seed_product):
    wishlist_services.add_to_wishlist(
        user_id=new_user.id, product_id=seed_product.id, vendor_id=new_user.id
    )
    removed = wishlist_services.remove_from_wishlist(new_user.id, seed_product.id)
    assert removed is not None

    wishlist = wishlist_services.get_user_wishlist(new_user.id)
    assert len(wishlist) == 0


def test_clear_wishlist(app, client, new_user, seed_product):
    wishlist_services.add_to_wishlist(
        user_id=new_user.id, product_id=seed_product.id, vendor_id=new_user.id
    )
    wishlist_services.clear_wishlist(new_user.id)
    wishlist = wishlist_services.get_user_wishlist(new_user.id)
    assert len(wishlist) == 0
