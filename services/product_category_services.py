from repo import product_category_repo
from models.product_category import ProductCategories
from instance.database import db


def assign_category(product_id: int, category_id: int):
    # Prevent duplicate assignment
    existing = ProductCategories.query.filter_by(
        product_id=product_id, category_id=category_id
    ).first()
    if existing:
        return None  # Already exists
    try:
        result = product_category_repo.assign_category_to_product(
            product_id, category_id
        )
        db.session.commit()
        return result
    except Exception:
        db.session.rollback()
        raise


def get_product_categories(product_id: int):
    return product_category_repo.get_categories_by_product(product_id)


def remove_category(product_id, category_id):
    try:
        result = product_category_repo.remove_category_from_product(
            product_id, category_id
        )
        db.session.commit()
        return result
    except Exception:
        db.session.rollback()
        raise
