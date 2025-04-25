from instance.database import db
from models.product_category import ProductCategories

def assign_category_to_product(product_id, category_id):
    relation = ProductCategories(product_id=product_id, category_id=category_id)
    db.session.add(relation)
    try:
        db.session.commit()
        return relation
    except:
        db.session.rollback()
        return None

def get_categories_by_product(product_id):
    return ProductCategories.query.filter_by(product_id=product_id).all()

def remove_category_from_product(product_id, category_id):
    relation = ProductCategories.query.filter_by(
        product_id=product_id,
        category_id=category_id
    ).first()
    if relation:
        db.session.delete(relation)
        db.session.commit()
        return True
    return False
