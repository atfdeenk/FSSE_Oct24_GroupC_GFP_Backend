from werkzeug.security import generate_password_hash, check_password_hash
from repo import user_repo
from models.user import Users
from models.product import Products
from models.feedback import Feedbacks
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import get_jwt_identity
from repo.user_repo import get_user_by_id
from flask import jsonify
from instance.database import db
from utils.security import hash_password
from decimal import Decimal

from models.user import RoleType


def create_user(data):
    try:
        data["password_hash"] = hash_password(data["password"])
        del data["password"]

        # ✅ Convert role string to Enum
        try:
            data["role"] = RoleType(data["role"])
        except KeyError:
            raise ValueError("Missing required field: role")

        user = user_repo.create_user(data)
        db.session.commit()  # Commit after adding user
        return user, None
    except IntegrityError as e:
        print("IntegrityError:", e)  # Debug output
        db.session.rollback()
        return None, "User with this email or username already exists."
    except Exception as e:
        print("Exception in create_user:", e)
        db.session.rollback()
        return None, "Failed to create user due to server error."


def authenticate(email, password):
    user = user_repo.get_user_by_email(email)
    if user and check_password_hash(user.password_hash, password):
        return user
    return None


def get_user_by_id(user_id):
    return user_repo.get_user_by_id(user_id)


def update_user(user_id, data, current_user_id, current_user_role):
    user = user_repo.get_user_by_id(user_id)

    if not user:
        return None, "User not found"

    if current_user_id != user.id and current_user_role != "admin":
        return None, "Unauthorized"

    protected_fields = ["role", "username"]
    if current_user_role != "admin":
        for field in protected_fields:
            data.pop(field, None)

    updated_user = user_repo.update_user(user, data)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return None, "Failed to update user"

    return updated_user, None


def get_all_users():
    return user_repo.get_all_users()


def delete_user(target_user_id, current_user_id, current_user_role):
    if current_user_role != "admin" and current_user_id != target_user_id:
        return None, "Unauthorized"

    user = Users.query.get(target_user_id)
    if not user:
        return None, "User not found"

    deleted_products_count = 0

    if user.role.value == "vendor":
        # Step 1: Delete all products belonging to this vendor
        products = Products.query.filter_by(vendor_id=user.id).all()
        deleted_products_count = len(products)

        for product in products:
            # 🆕 Step 1A: Delete feedbacks linked to this product first
            db.session.query(Feedbacks).filter_by(product_id=product.id).delete()

            # 🆕 Step 1B: Now safe to delete the product
            db.session.delete(product)

    # Step 2: Delete the user itself
    db.session.delete(user)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    # Step 3: Return success message
    if deleted_products_count > 0:
        return {
            "message": f"Seller and {deleted_products_count} product(s) deleted successfully"
        }, None
    else:
        return {"message": "User deleted successfully"}, None


def get_me_service():
    # Get the current user's ID from the JWT token
    current_user = (
        get_jwt_identity()
    )  # This will return a dictionary with user info (id, role, etc.)

    # Fetch the user data from the repository (or database)
    user = get_user_by_id(current_user["id"])

    if not user:
        return (
            jsonify({"message": "User not found"}),
            404,
        )  # Return the response in JSON format

    # Return the user's information (you can return just a subset of the fields)
    return (
        jsonify(
            {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": user.role,  # Assuming 'role' is a string or enum
            }
        ),
        200,
    )


def get_all_non_admin_users():
    return user_repo.get_users_exclude_role("admin")


def get_admin_users():
    return user_repo.get_users_by_role("admin")


def get_user_by_id_with_admin_check(target_user_id, current_user_role):
    user = user_repo.get_user_by_id(target_user_id)
    if not user:
        return None, "User not found"

    if user.role.value == "admin" and current_user_role != "admin":
        return None, "Unauthorized to view admin accounts"

    return user, None


def get_user_balance_service(
    user_id: int, current_user_id: int, current_user_role: str
):
    user = user_repo.get_user_by_id(user_id)
    if not user:
        return None, "User not found"

    if current_user_id != user.id and current_user_role != "admin":
        return None, "Unauthorized"

    return user.balance or 0.0, None


def update_my_balance_service(user_id: int, new_balance: float):
    user = user_repo.get_user_by_id(user_id)

    if not user:
        return None, "User not found"

    updated_user = user_repo.update_user_balance(user_id, Decimal(str(new_balance)))

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return None, "Failed to update balance"

    return updated_user, None
