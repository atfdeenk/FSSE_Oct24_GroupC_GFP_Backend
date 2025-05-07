from flask import current_app, abort, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from flask_jwt_extended.exceptions import NoAuthorizationError
from models.product import Products
from instance.database import db
from repo import product_repo
from decimal import Decimal
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from shared.cache import cache

def clear_all_product_list_cache():
    for page in range(1, 6): 
        print(f"⛔ Deleting page {page}") # adjust range if needed
        cache.delete_memoized(
            get_all_serialized_products,
            None, None, page, 10, "created_at", "desc"
        )
        cache.delete_memoized(
            get_all_serialized_products,
            None, None, page, 10, "price", "asc"
        )

def serialize_product(product: Products) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "description": product.description,
        "currency": product.currency,
        "price": (
            float(product.price)
            if isinstance(product.price, Decimal)
            else product.price
        ),
        "discount_percentage": product.discount_percentage,
        "stock_quantity": product.stock_quantity,
        "unit_quantity": product.unit_quantity,
        "image_url": product.image_url,
        "location": product.location,
        "featured": product.featured,
        "flash_sale": product.flash_sale,
        "vendor_id": product.vendor_id,
        "vendor_name": (
            product.vendor.username if product.vendor else None
        ),  # ✅ ADD THIS LINE
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
        "is_approved": product.is_approved,  # ✅ Expose for frontend

        "categories": [
            {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
            }
            for category in product.categories_linked
        ],
    }

@cache.cached(timeout=60, query_string=True)
def get_all_serialized_products(
    search=None,
    category_id=None,
    page=1,
    limit=10,
    sort_by="created_at",
    sort_order="desc",
):
    print("[CACHE MISS] Fetching products from DB...")

    # Allow JWT if available
    try:
        verify_jwt_in_request()
        claims = get_jwt()
        user_id = get_jwt_identity()
    except NoAuthorizationError:
        claims = {}
        user_id = None

    role = claims.get("role") if claims else None  # ✅ ADD THIS LINE


    include_unapproved = request.args.get("include_unapproved") == "true"

    # ✅ Only allow include_unapproved for admin or vendor
    if include_unapproved and role not in ["admin"]:
        include_unapproved = False

    products, total = product_repo.get_all_products_filtered(
        search=search,
        category_id=category_id,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        include_unapproved=include_unapproved,
        current_user_id=user_id,
        current_user_role=role,
    )

    return {
        "products": [serialize_product(p) for p in products],
        "total": total,
        "page": page,
        "limit": limit,
    }



def get_paginated_serialized_products(page: int, limit: int):
    paginated = product_repo.get_paginated_products(page, limit)
    products = [serialize_product(p) for p in paginated.items]
    return {
        "products": products,
        "total": paginated.total,
        "page": paginated.page,
        "pages": paginated.pages,
        "limit": paginated.per_page,
    }

@cache.cached(timeout=300)
def get_serialized_product_by_id(product_id: int):
    product = product_repo.get_product_by_id(product_id)
    if not product or not product.is_approved:
        return None
    return serialize_product(product)


def create_product_with_serialization(data: dict):
    claims = get_jwt()
    vendor_id = claims.get("sub")
    vendor_city = claims.get("city", "Unknown")
    data["vendor_id"] = vendor_id
    data["location"] = vendor_city

    try:
        data["price"] = Decimal(data["price"])
    except Exception as e:
        print(f"[PRICE ERROR] {e}")
        abort(400, "Invalid price format")

    data.pop("location", None)
    data.setdefault("image_url", "http://example.com/image.jpg")
    data.setdefault("featured", False)
    data.setdefault("flash_sale", False)

    print("[DEBUG] Final product payload BEFORE commit:", data)

    try:
        product = product_repo.create_product(data)
        if not product:
            print("[DEBUG] product_repo.create_product returned None")
            abort(409, "Duplicate slug. Product already exists.")

        db.session.commit()

        # ✅ Invalidate cached /products list
        clear_all_product_list_cache()

        return serialize_product(product)

    except HTTPException as e:
        raise e
    except IntegrityError as e:
        db.session.rollback()
        print("[INTEGRITY ERROR DURING PRODUCT CREATION]")
        print(e)
        abort(409, "Duplicate slug. Product already exists.")
    except Exception as e:
        db.session.rollback()
        print("[CRITICAL ERROR DURING PRODUCT CREATION]")
        print(e)
        abort(500, f"Server Error: {str(e)}")

def update_product_with_serialization(product_id: int, data: dict):
    product = product_repo.update_product(product_id, data)
    if not product:
        return None
    try:
        db.session.commit()

        clear_all_product_list_cache()

    except Exception:
        db.session.rollback()
        raise
    return serialize_product(product)


def delete_product_and_return_message(product_id: int):
    product = product_repo.delete_product(product_id)
    if not product:
        return None
    try:
        db.session.commit()

        clear_all_product_list_cache()

    except Exception:
        db.session.rollback()
        raise
    return {"message": "Product deleted"}


def approve_product_by_id(product_id: int):
    product = product_repo.approve_product(product_id)
    if not product:
        raise ValueError("Product not found")
    try:
        db.session.commit()

        clear_all_product_list_cache()

    except Exception:
        db.session.rollback()
        raise
    return serialize_product(product)



        # Add more common combos (search/category) if needed

        # You can add more common variations if needed
