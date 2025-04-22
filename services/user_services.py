from werkzeug.security import generate_password_hash, check_password_hash
from repo import user_repo
from models.user import Users
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import get_jwt_identity
from repo.user_repo import get_user_by_id
from flask import jsonify

def create_user(data):
    try:
        hashed_password = generate_password_hash(data["password"])
        data["password_hash"] = hashed_password
        del data["password"]  # remove plain password
        user = user_repo.create_user(data)
        return user
    except IntegrityError:
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


def delete_user(user_id, current_user):
    user = user_repo.get_user_by_id(user_id)
    if not user:
        return None, "User not found"

    # Only admin can delete users
    if current_user["role"] != "admin":
        return None, "Unauthorized"

    user_repo.delete_user(user)
    return user, None

def get_me_service():
    # Get the current user's ID from the JWT token
    current_user = get_jwt_identity()  # This will return a dictionary with user info (id, role, etc.)

    # Fetch the user data from the repository (or database)
    user = get_user_by_id(current_user["id"])

    if not user:
        return jsonify({"message": "User not found"}), 404  # Return the response in JSON format

    # Return the user's information (you can return just a subset of the fields)
    return jsonify({
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "role": user.role  # Assuming 'role' is a string or enum
    }), 200  # Ensure it always returns a tuple with status code
