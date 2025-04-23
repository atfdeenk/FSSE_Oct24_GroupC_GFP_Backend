from repo import cart_repo, cart_item_repo

def get_or_create_cart(user_id):
    cart = cart_repo.get_cart_by_user(user_id)
    if not cart:
        cart = cart_repo.create_cart_for_user(user_id)
    return cart

def add_item_to_cart(user_id, product_id, quantity):
    cart = get_or_create_cart(user_id)
    return cart_item_repo.add_cart_item(cart.id, product_id, quantity)
