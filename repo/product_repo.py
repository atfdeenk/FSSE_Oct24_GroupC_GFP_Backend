from instance.database import db
from models.product import Products
from models.product_category import ProductCategories
from models.cart_item import CartItems
from sqlalchemy.exc import IntegrityError

def get_all_products():
    return Products.query.all()

def get_product_by_id(product_id):
    return Products.query.get(product_id)

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
    product = Products.query.get(product_id)
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

    # ✅ Delete all cart items related to this product
    CartItems.query.filter_by(product_id=product_id).delete()

    db.session.delete(product)
    db.session.commit()
    return product
