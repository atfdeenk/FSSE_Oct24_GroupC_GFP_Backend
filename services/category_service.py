# services/category_services.py

from sqlalchemy.exc import IntegrityError
from repo import category_repo
from models.category import Categories


def create_category(data, current_user):
    try:
        data["vendor_id"] = current_user["id"]  # associate with logged-in vendor
        category = category_repo.create_category(data)
        return category
    except IntegrityError:
        return None


def get_all_categories():
    return category_repo.get_all_categories()


def get_category_by_id(category_id):
    return category_repo.get_category_by_id(category_id)


def update_category(category_id, data, current_user):
    category = category_repo.get_category_by_id(category_id)
    if not category:
        return None, "Category not found"

    # Handle current_user as string or dict
    if isinstance(current_user, str):
        current_user_id = int(current_user)
        current_user_role = None
    else:
        current_user_id = current_user.get("id")
        current_user_role = current_user.get("role")

    # Only the owner or admin can update
    if category.vendor_id != current_user_id and current_user_role != "admin":
        return None, "Unauthorized"

    updated_category = category_repo.update_category(category, data)
    return updated_category, None


def delete_category(category_id, current_user):
    category = category_repo.get_category_by_id(category_id)
    if not category:
        return None, "Category not found"

    # Handle current_user as string or dict
    if isinstance(current_user, str):
        current_user_id = int(current_user)
        current_user_role = None
    else:
        current_user_id = current_user.get("id")
        current_user_role = current_user.get("role")

    # Only the owner or admin can delete
    if category.vendor_id != current_user_id and current_user_role != "admin":
        return None, "Unauthorized"

    category_repo.delete_category(category)
    return category, None
