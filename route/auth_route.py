import os
import time
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from services import user_services
from services.user_services import get_me_service
from shared.auth import role_required
from marshmallow import Schema, fields, ValidationError

auth_bp = Blueprint("auth_bp", __name__)


# Define input schema for user registration and update
class UserSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    phone = fields.Str(required=False)  # true
    role = fields.Str(required=True)
    date_of_birth = fields.Str(required=False)
    address = fields.Str(required=False)
    city = fields.Str(required=False)
    state = fields.Str(required=False)
    zip_code = fields.Str(required=False)
    country = fields.Str(required=False)
    image_url = fields.Str(required=False)
    bank_account = fields.Str(required=False)
    bank_name = fields.Str(required=False)


user_schema = UserSchema(partial=True)  # partial=True allows partial updates


# Public: anyone can register
@auth_bp.route("/register", methods=["POST"])
def register():
    if not request.is_json:
        return jsonify({"msg": "Invalid content type"}), 400
    data = request.get_json()
    try:
        validated_data = user_schema.load(data)
    except ValidationError as err:
        # Return detailed validation errors for debugging
        return jsonify({"msg": "Validation error", "errors": err.messages}), 400

    user, error = user_services.create_user(validated_data)
    if error:
        # Return detailed error message from service
        return jsonify({"msg": error}), 400
    if not user:
        return jsonify({"msg": "User registration failed"}), 400
    return jsonify({"msg": "User registered successfully"}), 201


# Public: anyone can log in
@auth_bp.route("/login", methods=["POST"])
def login():
    overall_start = time.perf_counter()

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    step1 = time.perf_counter()
    user = user_services.authenticate(email, password)
    step2 = time.perf_counter()

    if not user:
        if os.getenv("FLASK_ENV") == "development":
            print(f"[LOGIN] User not found or wrong password (in {step2 - step1:.3f}s)")
        return jsonify({"msg": "Invalid credentials"}), 401

    # Refresh from DB
    step3 = time.perf_counter()
    user = user_services.get_user_by_id(user.id)
    step4 = time.perf_counter()

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role.value, "city": user.city or "Unknown"},
    )
    step5 = time.perf_counter()

    if os.getenv("FLASK_ENV") == "development":
        print(f"[LOGIN] Auth lookup: {step2 - step1:.3f}s")
        print(f"[LOGIN] Refresh user: {step4 - step3:.3f}s")
        print(f"[LOGIN] Token creation: {step5 - step4:.3f}s")
        print(f"[LOGIN] Total: {step5 - overall_start:.3f}s")

    return jsonify(access_token=token), 200


# Private: any authenticated user can access their own info
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = user_services.get_user_by_id(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    return (
        jsonify(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "role": user.role.value,
                "image_url": user.image_url,
                "address": user.address,
                "city": user.city,
                "state": user.state,
                "zip_code": user.zip_code,
                "country": user.country,
            }
        ),
        200,
    )


# Private: Only the user themselves or admin can update a user
@auth_bp.route("/users/<int:user_id>", methods=["PUT", "PATCH"])
@jwt_required()
@role_required("vendor", "customer", "admin")  # Optional: restrict to known roles
def update_user(user_id):
    if not request.is_json:
        return jsonify({"msg": "Invalid content type"}), 400
    data = request.get_json()

    # Validate input data
    try:
        validated_data = user_schema.load(data, partial=True)
    except ValidationError as err:
        return jsonify({"msg": "Validation error", "errors": err.messages}), 400

    current_user_id = int(get_jwt_identity())
    current_user_role = get_jwt().get("role")
    user, error = user_services.update_user(
        user_id, validated_data, current_user_id, current_user_role
    )

    if error:
        return jsonify({"msg": error}), 403 if error == "Unauthorized" else 404

    return jsonify({"msg": "User updated successfully"}), 200


@auth_bp.route("/users/all", methods=["GET"])
@jwt_required()
@role_required("admin")  # Admin-only
def get_all_users():
    users = user_services.get_all_users()
    return (
        jsonify(
            [
                {
                    "id": u.id,
                    "username": u.username,
                    "email": u.email,
                    "role": u.role.value,
                    "is_active": u.is_active,
                    "created_at": u.created_at.isoformat(),
                }
                for u in users
            ]
        ),
        200,
    )


@auth_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
@role_required("vendor", "customer", "admin")
def delete_user(user_id):
    current_user_id = int(get_jwt_identity())
    current_user_role = get_jwt().get("role")

    response_message, error = user_services.delete_user(
        user_id, current_user_id, current_user_role
    )

    if error:
        return jsonify({"msg": error}), 403 if error == "Unauthorized" else 404

    return jsonify(response_message), 200


@auth_bp.route("/users", methods=["GET"])
@jwt_required()
def get_all_non_admin_users():
    users = user_services.get_all_non_admin_users()
    return (
        jsonify(
            [
                {
                    "id": u.id,
                    "username": u.username,
                    "city": u.city,
                    "image_url": u.image_url,
                    "role": u.role.value,
                }
                for u in users
            ]
        ),
        200,
    )


@auth_bp.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user_by_id(user_id):
    current_user_role = get_jwt().get("role")

    user, error = user_services.get_user_by_id_with_admin_check(
        user_id, current_user_role
    )
    if error:
        return jsonify({"msg": error}), (
            403 if error == "Unauthorized to view admin accounts" else 404
        )

    return (
        jsonify(
            {
                "id": user.id,
                "username": user.username,
                "city": user.city,
                "image_url": user.image_url,
                "role": user.role.value,
            }
        ),
        200,
    )


@auth_bp.route("/users/admins", methods=["GET"])
@jwt_required()
@role_required("admin")
def get_admin_users():
    users = user_services.get_admin_users()
    return (
        jsonify(
            [
                {
                    "id": u.id,
                    "username": u.username,
                    "city": u.city,
                    "image_url": u.image_url,
                    "role": u.role.value,
                }
                for u in users
            ]
        ),
        200,
    )


@auth_bp.route("/users/me/balance", methods=["GET"])
@jwt_required()
@role_required("customer", "vendor")
def get_my_balance():
    current_user_id = int(get_jwt_identity())

    user = user_services.get_user_by_id(current_user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    return jsonify({"balance": float(user.balance or 0.0)}), 200


@auth_bp.route("/users/me/balance", methods=["PATCH"])
@jwt_required()
@role_required("customer", "vendor")
def update_my_balance():
    if not request.is_json:
        return jsonify({"msg": "Invalid content type"}), 400
    data = request.get_json()
    new_balance = data.get("balance")

    if new_balance is None:
        return jsonify({"msg": "Missing balance value"}), 400

    if new_balance < 0:
        return jsonify({"msg": "Balance cannot be negative"}), 400

    current_user_id = int(get_jwt_identity())

    updated_user, error = user_services.update_my_balance_service(
        current_user_id, new_balance
    )

    if error:
        return jsonify({"msg": error}), 404

    return (
        jsonify(
            {
                "msg": "Balance updated successfully",
                "balance": float(updated_user.balance),
            }
        ),
        200,
    )
