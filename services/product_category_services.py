from repo import product_category_repo
from models.product_category import ProductCategories

def assign_category(product_id: int, category_id: int):
    # Prevent duplicate assignment
    existing = ProductCategories.query.filter_by(
        product_id=product_id, category_id=category_id
    ).first()
    if existing:
        return None  # Already exists

    return product_category_repo.assign_category_to_product(product_id, category_id)

def get_product_categories(product_id: int):
    return product_category_repo.get_categories_by_product(product_id)

def remove_category(product_id: int, category_id: int):
    return product_category_repo.remove_category_from_product(product_id, category_id)
