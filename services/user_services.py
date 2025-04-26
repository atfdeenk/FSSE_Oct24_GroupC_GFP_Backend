from werkzeug.security import generate_password_hash, check_password_hash
from repo import user_repo
from models.user import Users
from models.product import Products
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import get_jwt_identity
from repo.user_repo import get_user_by_id
from flask import jsonify
from instance.database import db

from models.user import RoleType


def create_user(data):
    try:
        # ✅ Hash the password
        hashed_password = generate_password_hash(data["password"])
        data["password_hash"] = hashed_password
        del data["password"]

        # ✅ Convert role string to Enum
        try:
            data["role"] = RoleType(data["role"])
        except KeyError:
            raise ValueError("Missing required field: role")

        user = user_repo.create_user(data)
        return user
    except IntegrityError as e:
        print("IntegrityError:", e)  # Debug output
        return None


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

    # Only the user themselves or an admin can update
    if current_user_id != user.id and current_user_role != "admin":
        return None, "Unauthorized"

    # Prevent email/username/role overwrite unless admin
    protected_fields = ["role", "email", "username"]
    if current_user_role != "admin":
        for field in protected_fields:
            data.pop(field, None)

    updated_user = user_repo.update_user(user, data)
    return updated_user, None


def get_all_users():
    return user_repo.get_all_users()


def delete_user(target_user_id, current_user_id, current_user_role):
    if current_user_role != "admin" and current_user_id != target_user_id:
        return None, "Unauthorized"

    user = Users.query.get(target_user_id)
    if not user:
        return None, "User not found"

    # ✅ Block deletion if vendor has products
    if user.role.value == "vendor":
        product_count = Products.query.filter_by(vendor_id=user.id).count()
        if product_count > 0:
            return None, "Cannot delete vendor with existing products"

    db.session.delete(user)
    db.session.commit()
    return user, None


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
    )  # Ensure it always returns a tuple with status code
