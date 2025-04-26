from repo import cart_repo, cart_item_repo

def get_cart_items(user_id):
    cart = cart_repo.get_cart_by_user(user_id)
    return cart_item_repo.get_cart_items(cart.id) if cart else []

def add_item(user_id, product_id, quantity):
    cart = cart_repo.get_cart_by_user(user_id)
    if not cart:
        cart = cart_repo.create_cart_for_user(user_id)
    return cart_item_repo.add_cart_item(cart.id, product_id, quantity)

def update_item(cart_item_id, quantity):
    return cart_item_repo.update_cart_item_quantity(cart_item_id, quantity)

def delete_item(cart_item_id):
    return cart_item_repo.remove_cart_item(cart_item_id)
