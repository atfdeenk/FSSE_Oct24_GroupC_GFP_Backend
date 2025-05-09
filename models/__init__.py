from .user import Users
from .category import Categories

from .cart import Cart
from .cart_item import CartItems

from .order import Orders
from .order_item import OrderItems

from .product import Products
from .product_category import ProductCategories
from .product_image import ProductImages
from .feedback import Feedbacks

from .wishlist_item import WishlistItems
from .voucher import Vouchers


Product = Products
ProductCategory = ProductCategories  # <-- ADD THIS LINE


__all__ = [
    "Users",
    "Categories",
    "Cart",
    "CartItems",
    "Orders",
    "OrderItems",
    "Products",
    "ProductCategories",
    "ProductImages",
    "Feedbacks",
    "WishlistItems",
    "Vouchers",
]
