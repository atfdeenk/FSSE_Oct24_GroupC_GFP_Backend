from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from services import user_services
from services.user_services import get_me_service
from shared.auth import role_required  

auth_bp = Blueprint("auth_bp", __name__)

# Public: anyone can register
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    user = user_services.create_user(data)
    if not user:
        return jsonify({"msg": "User registration failed"}), 400
    return jsonify({"msg": "User created successfully"}), 201

# Public: anyone can log in
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = user_services.authenticate(data["email"], data["password"])
    if not user:
        return jsonify({"msg": "Invalid credentials"}), 401

    token = create_access_token(identity={"id": user.id, "role": user.role.value})
    return jsonify({"access_token": token}), 200

# Private: any authenticated user can access their own info
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_info = get_jwt_identity()
    return jsonify(user_info), 200

# Private: Only the user themselves or admin can update a user
@auth_bp.route("/users/<int:user_id>", methods=["PUT", "PATCH"])
@jwt_required()
@role_required("admin", "vendor", "customer")  # Optional: restrict to known roles
def update_user(user_id):
    data = request.get_json()
    
    current_user_id = int(get_jwt_identity())
    current_user_role = get_jwt().get("role")
    user, error = user_services.update_user(user_id, data, current_user_id, current_user_role)


    if error:
        return jsonify({"msg": error}), 403 if error == "Unauthorized" else 404

    return jsonify({"msg": "User updated successfully"}), 200


@auth_bp.route("/users", methods=["GET"])
@jwt_required()
@role_required("admin")  # Admin-only
def get_all_users():
    users = user_services.get_all_users()
    return jsonify([{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "role": u.role.value,
        "is_active": u.is_active,
        "created_at": u.created_at.isoformat()
    } for u in users]), 200

@auth_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def delete_user(user_id):
    current_user = get_jwt_identity()
    user, error = user_services.delete_user(user_id, current_user)

    if error:
        return jsonify({"msg": error}), 403 if error == "Unauthorized" else 404

    return jsonify({"msg": "User deleted successfully"}), 200
