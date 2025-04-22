from instance.database import db
from models.product import Products
from sqlalchemy.exc import IntegrityError

def get_all_products():
    return Products.query.all()

def get_product_by_id(product_id):
    return Products.query.get(product_id)

def create_product(data):
    try:
        print("[DEBUG] raw data:", data)
        product = Products(**data)
        db.session.add(product)
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
    db.session.delete(product)
    db.session.commit()
    return product
