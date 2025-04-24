from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from shared.auth import role_required
from services.product_services import (
    get_all_serialized_products,
    get_serialized_product_by_id,
    create_product_with_serialization,
    update_product_with_serialization,
    delete_product_and_return_message,
)

product_bp = Blueprint('product_bp', __name__)

@product_bp.route("/products", methods=["GET"])
def get_all_products():
    search = request.args.get("search")
    category_id = request.args.get("category_id", type=int)
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)
    sort_by = request.args.get("sort_by", default="created_at", type=str)
    sort_order = request.args.get("sort_order", default="desc", type=str)


    products = get_all_serialized_products(
        search=search,
        category_id=category_id,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return jsonify(products), 200


@product_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = get_serialized_product_by_id(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    return jsonify(product), 200

@product_bp.route("/products", methods=["POST"])
@jwt_required()
@role_required("vendor", "admin")
def create_product():
    print("🟢 ENTERED PRODUCT POST ROUTE")
    if not request.is_json:
        print("❌ Not JSON")
        return jsonify({"msg": "Invalid content type"}), 400
    data = request.get_json()
    print("✅ JSON payload received:", data)
    product = create_product_with_serialization(data)
    if not product:
        return jsonify({"message": "Error creating product (possibly slug conflict)"}), 400
    return jsonify(product), 201


@product_bp.route("/products/<int:product_id>", methods=["PUT"])
@jwt_required()
@role_required("vendor", "admin")
def update_product(product_id):
    data = request.get_json()
    product = update_product_with_serialization(product_id, data)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    return jsonify(product), 200

@product_bp.route("/products/<int:product_id>", methods=["DELETE"])
@jwt_required()
@role_required("vendor", "admin")
def delete_product(product_id):
    result = delete_product_and_return_message(product_id)
    if not result:
        return jsonify({"message": "Product not found"}), 404
    return jsonify(result), 200
