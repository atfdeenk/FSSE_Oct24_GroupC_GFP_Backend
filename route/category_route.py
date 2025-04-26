from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from shared.auth import role_required
from services import category_service

category_bp = Blueprint("category_bp", __name__)


# Public: Get all categories
@category_bp.route("/categories", methods=["GET"])
def get_all_categories():
    categories = category_service.get_all_categories()
    return (
        jsonify(
            [
                {
                    "id": c.id,
                    "name": c.name,
                    "slug": c.slug,
                    "image_url": c.image_url,
                    "vendor_id": c.vendor_id,
                    "parent_id": c.parent_id,
                }
                for c in categories
            ]
        ),
        200,
    )


# Public: Get a specific category by ID
@category_bp.route("/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):
    category = category_service.get_category_by_id(category_id)
    if not category:
        return jsonify({"msg": "Category not found"}), 404
    return (
        jsonify(
            {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "image_url": category.image_url,
                "vendor_id": category.vendor_id,
                "parent_id": category.parent_id,
            }
        ),
        200,
    )


# Protected: Vendor/Admin can create a category
@category_bp.route("/categories", methods=["POST"])
# @jwt_required()
@role_required("vendor", "admin")
def create_category():
    data = request.get_json()
    current_user = get_jwt_identity()
    category = None
    error = None
    try:
        # Debug log for incoming data
        print(f"Create category request data: {data}")
        category, error = category_service.create_category(data, current_user)
    except Exception as e:
        error = str(e)
        print(f"Error creating category: {error}")
    if error or not category:
        return jsonify({"msg": error or "Failed to create category"}), 400
    return jsonify({"msg": "Category created", "id": category.id}), 201


# Protected: Vendor/Admin can update a category
@category_bp.route("/categories/<int:category_id>", methods=["PUT"])
# @jwt_required()
@role_required("vendor", "admin")
def update_category(category_id):
    data = request.get_json()
    current_user = get_jwt_identity()
    category, error = category_service.update_category(category_id, data, current_user)
    if error:
        return jsonify({"msg": error}), 403 if error == "Unauthorized" else 404
    return jsonify({"msg": "Category updated"}), 200


# Protected: Vendor/Admin can delete a category
@category_bp.route("/categories/<int:category_id>", methods=["DELETE"])
# @jwt_required()
@role_required("vendor", "admin")
def delete_category(category_id):
    current_user = get_jwt_identity()
    category, error = category_service.delete_category(category_id, current_user)
    if error:
        return jsonify({"msg": error}), 403 if error == "Unauthorized" else 404
    return jsonify({"msg": "Category deleted"}), 200
