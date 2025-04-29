from instance.database import db
from models.product import Products
from models.product_category import ProductCategories
from models.category import Categories
from models.cart_item import CartItems
from models.user import Users
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy import asc, desc, cast, Numeric, or_

def get_all_products():
    return Products.query.all()

def get_product_by_id(product_id):
    return Products.query.get(product_id)

def get_paginated_products(page: int, limit: int):
    return Products.query.paginate(page=page, per_page=limit, error_out=False)

def create_product(data):
    try:
        print("[DEBUG] raw data:", data)
        category_ids = data.pop("category_ids", [])  # Extract category_ids
        product = Products(**data)
        db.session.add(product)
        db.session.flush()  # Get product.id before commit

        # Create product-category mappings
        for cid in category_ids:
            db.session.add(ProductCategories(product_id=product.id, category_id=cid))

        db.session.commit()
        print("[DEBUG] product created:", product)
        return product
    except Exception as e:
        db.session.rollback()
        print("[DB ERROR]", e)
        raise e



def update_product(product_id, data):
    # Replace deprecated Query.get() with Session.get()
    product = db.session.get(Products, product_id)
    if not product:
        return None
    for key, value in data.items():
        if hasattr(product, key):
            setattr(product, key, value)
    db.session.commit()
    return product

def delete_product(product_id):
    product = Products.query.get(product_id)
    if not product:
        return None

    # ❌ REMOVE this line; let cascade handle it
    # ProductCategories.query.filter_by(product_id=product_id).delete()

    CartItems.query.filter_by(product_id=product_id).delete()
    db.session.delete(product)
    db.session.commit()
    return product


from sqlalchemy.orm import aliased

def get_all_products_filtered(search=None, category_id=None, page=1, limit=10, sort_by="created_at", sort_order="desc"):
    query = Products.query.filter(Products.is_approved == True)

    if search:
        # ✅ Join Users table first
        query = query.join(Users, Products.vendor_id == Users.id)

        query = query.filter(
            or_(
                Products.name.ilike(f"%{search}%"),
                Users.city.ilike(f"%{search}%"),  # ✅ search on Users.city not Products.location
            )
        )

    if category_id:
        query = query.join(ProductCategories).filter(ProductCategories.category_id == category_id)

    # Sorting logic
    if sort_by == "price":
        sort_column = cast(Products.price, Numeric)
    elif sort_by == "name":
        sort_column = Products.name
    elif sort_by == "created_at":
        sort_column = Products.created_at
    else:
        sort_column = Products.created_at  # Fallback

    order_func = asc if sort_order.lower() == "asc" else desc
    query = query.order_by(order_func(sort_column))

    total = query.count()
    products = query.offset((page - 1) * limit).limit(limit).all()

    print("[DEBUG] Sort By:", sort_by)
    print("[DEBUG] Sort Order:", sort_order)

    return products, total

def approve_product(product_id: int) -> Products:
    product = db.session.get(Products, product_id)
    if not product:
        return None
    product.is_approved = True
    db.session.commit()
    return product
