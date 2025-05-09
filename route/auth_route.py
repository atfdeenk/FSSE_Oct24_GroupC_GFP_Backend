import os
import time
from flask import Blueprint, request, jsonify, current_app  # add current_app
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
from shared.limiter import limiter


auth_bp = Blueprint("auth_bp", __name__)


# Define input schema for user registration and update
class UserSchema(Schema):
    username = fields.Str(required=False)
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
@limiter.limit("5 per minute")
def register():
    current_app.logger.info("Register endpoint called")
    if not request.is_json:
        current_app.logger.warning("Register: Invalid content type")
        return jsonify({"msg": "Invalid content type"}), 400
    data = request.get_json()
    try:
        validated_data = user_schema.load(data)
    except ValidationError as err:
        current_app.logger.warning(f"Register: Validation error - {err.messages}")
        return jsonify({"msg": "Validation error", "errors": err.messages}), 400

    user, error = user_services.create_user(validated_data)
    if error:
        current_app.logger.error(f"Register: {error}")
        return jsonify({"msg": error}), 400
    if not user:
        current_app.logger.error("Register: User registration failed")
        return jsonify({"msg": "User registration failed"}), 400
    current_app.logger.info(
        f"Register: User {user.username if user else 'unknown'} registered successfully"
    )
    return jsonify({"msg": "User registered successfully"}), 201


# Public: anyone can log in
@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    current_app.logger.info("Login endpoint called")
    overall_start = time.perf_counter()

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    step1 = time.perf_counter()
    user = user_services.authenticate(email, password)
    step2 = time.perf_counter()

    if not user:
        current_app.logger.warning(f"Login failed for email: {email}")
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

    current_app.logger.info(f"Login successful for user_id: {user.id}")

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
    current_app.logger.info("Me endpoint called")
    user_id = int(get_jwt_identity())
    user = user_services.get_user_by_id(user_id)

    if not user:
        current_app.logger.warning(f"Me: User {user_id} not found")
        return jsonify({"msg": "User not found"}), 404

    current_app.logger.info(f"Me: User {user_id} info returned")
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
@limiter.limit("10 per minute")
@jwt_required()
@role_required("vendor", "customer", "admin")  # Optional: restrict to known roles
def update_user(user_id):
    current_app.logger.info(f"Update user endpoint called for user_id: {user_id}")
    if not request.is_json:
        current_app.logger.warning(f"Update user {user_id}: Invalid content type")
        return jsonify({"msg": "Invalid content type"}), 400
    data = request.get_json()

    # Validate input data
    try:
        validated_data = user_schema.load(data, partial=True)
    except ValidationError as err:
        current_app.logger.warning(
            f"Update user {user_id}: Validation error - {err.messages}"
        )
        return jsonify({"msg": "Validation error", "errors": err.messages}), 400

    current_user_id = int(get_jwt_identity())
    current_user_role = get_jwt().get("role")
    current_app.logger.info(
        f"User {current_user_id} ({current_user_role}) attempts to update user {user_id}"
    )
    user, error = user_services.update_user(
        user_id, validated_data, current_user_id, current_user_role
    )

    if error:
        current_app.logger.error(f"Update user {user_id} failed: {error}")
        return jsonify({"msg": error}), 403 if error == "Unauthorized" else 404

    current_app.logger.info(
        f"User {user_id} updated successfully by user {current_user_id}"
    )
    return jsonify({"msg": "User updated successfully"}), 200


@auth_bp.route("/users/all", methods=["GET"])
@jwt_required()
@role_required("admin")  # Admin-only
def get_all_users():
    current_app.logger.info("Get all users endpoint called")
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
    current_app.logger.info(f"Delete user endpoint called for user_id: {user_id}")
    current_user_id = int(get_jwt_identity())
    current_user_role = get_jwt().get("role")

    response_message, error = user_services.delete_user(
        user_id, current_user_id, current_user_role
    )

    if error:
        current_app.logger.error(f"Delete user {user_id} failed: {error}")
        return jsonify({"msg": error}), 403 if error == "Unauthorized" else 404

    current_app.logger.info(f"User {user_id} deleted by user {current_user_id}")
    return jsonify(response_message), 200


@auth_bp.route("/users", methods=["GET"])
@jwt_required()
def get_all_non_admin_users():
    current_app.logger.info("Get all non-admin users endpoint called")
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
    current_app.logger.info(f"Get user by id endpoint called for user_id: {user_id}")
    current_user_role = get_jwt().get("role")

    user, error = user_services.get_user_by_id_with_admin_check(
        user_id, current_user_role
    )
    if error:
        current_app.logger.warning(f"Get user by id {user_id} failed: {error}")
        return jsonify({"msg": error}), (
            403 if error == "Unauthorized to view admin accounts" else 404
        )

    current_app.logger.info(f"User {user_id} info returned")
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
    current_app.logger.info("Get admin users endpoint called")
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
    current_app.logger.info("Get my balance endpoint called")
    current_user_id = int(get_jwt_identity())

    user = user_services.get_user_by_id(current_user_id)
    if not user:
        current_app.logger.warning(f"Get my balance: User {current_user_id} not found")
        return jsonify({"msg": "User not found"}), 404

    current_app.logger.info(f"Balance for user {current_user_id} returned")
    return jsonify({"balance": float(user.balance or 0.0)}), 200


# ⚠️ Deprecated: use PATCH /request-topup/<id>/approve instead
@auth_bp.route("/users/<int:user_id>/balance", methods=["PATCH"])
@limiter.limit("5 per minute")
@jwt_required()
@role_required("admin")
def admin_update_user_balance(user_id):
    current_app.logger.info(f"Admin update balance for user_id: {user_id} called")

    if not request.is_json:
        return jsonify({"msg": "Invalid content type"}), 400

    data = request.get_json()
    added_amount = data.get("balance")

    if added_amount is None:
        return jsonify({"msg": "Missing balance value"}), 400

    if added_amount < 0:
        return jsonify({"msg": "Balance cannot be negative"}), 400

    updated_user, error = user_services.update_my_balance_service(user_id, added_amount)

    if error:
        return jsonify({"msg": error}), 404

    # ✅ Mark top-up request as approved in CSV
    # user_services.mark_topup_request_as_approved(user_id, added_amount)

    return (
        jsonify(
            {
                "msg": f"Balance updated for user {user_id}",
                "balance": float(updated_user.balance),
            }
        ),
        200,
    )


@auth_bp.route("/users/me/request-topup", methods=["POST"])
@jwt_required()
@role_required("customer", "vendor")
def request_topup():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    amount = data.get("amount")

    result, error = user_services.request_topup_service(current_user_id, amount)

    if error:
        return jsonify({"msg": error}), 400

    return (
        jsonify(
            {
                "msg": "Top-up request submitted. Please wait for admin approval.",
                "requested": result,
            }
        ),
        200,
    )


@auth_bp.route("/topup-requests", methods=["GET"])
@jwt_required()
@role_required("admin")
def view_topup_requests():
    logs, error = user_services.get_topup_requests_service()

    if error:
        return jsonify({"msg": error}), 500

    return jsonify({"requests": logs}), 200


@auth_bp.route("/request-topup/<int:request_id>/approve", methods=["POST"])
@jwt_required()
@role_required("admin")
def approve_topup(request_id):
    success, user_id, amount = user_services.mark_topup_request_status(
        request_id, "approved"
    )
    if not success:
        return jsonify({"msg": "Top-up request not found or already processed"}), 404

    updated_user, error = user_services.update_my_balance_service(user_id, amount)
    if error:
        return jsonify({"msg": error}), 404

    return (
        jsonify(
            {
                "msg": f"Top-up approved and balance updated for user {user_id}",
                "new_balance": float(updated_user.balance),
            }
        ),
        200,
    )


@auth_bp.route("/request-topup/<int:request_id>/reject", methods=["POST"])
@jwt_required()
@role_required("admin")
def reject_topup(request_id):
    success, user_id, _ = user_services.mark_topup_request_status(
        request_id, "rejected"
    )
    if not success:
        return jsonify({"msg": "Top-up request not found or already processed"}), 404

    return jsonify({"msg": f"Top-up request {request_id} rejected"}), 200
