from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from shared.auth import role_required
from services.product_services import (
    get_all_serialized_products,
    get_serialized_product_by_id,
    create_product_with_serialization,
    update_product_with_serialization,
    delete_product_and_return_message,
    approve_product_by_id,  # Add this if needed
)
import services.product_services as product_services
from marshmallow import Schema, fields, ValidationError
from shared.limiter import limiter

product_bp = Blueprint("product_bp", __name__)


# Define input schema for product creation and update
class ProductSchema(Schema):
    name = fields.Str(required=True)
    slug = fields.Str(required=True)
    description = fields.Str()
    currency = fields.Str()
    price = fields.Decimal(required=True)
    discount_percentage = fields.Float()
    stock_quantity = fields.Int()
    unit_quantity = fields.Str()
    image_url = fields.Str()
    location = fields.Str()
    featured = fields.Bool()
    flash_sale = fields.Bool()
    category_ids = fields.List(fields.Int())


product_schema = ProductSchema()


@product_bp.route("/products", methods=["GET"])
@limiter.limit("60 per minute")
def get_all_products():
    current_app.logger.info("GET /products called with args: %s", dict(request.args))
    search = request.args.get("search")
    category_id = request.args.get("category_id", type=int)
    category_slug = request.args.get("category", type=str)  # 🆕 Support category slug
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)
    sort_by = request.args.get("sort_by", default="created_at", type=str)
    sort_order = request.args.get("sort_order", default="desc", type=str)

    # 🆕 If frontend sends category slug
    if category_slug and not category_id:
        from models.category import Categories
        from instance.database import db

        category = db.session.query(Categories).filter_by(slug=category_slug).first()
        if category:
            category_id = category.id
        else:
            # If no matching category found, return empty list early
            return (
                jsonify({"products": [], "total": 0, "page": page, "limit": limit}),
                200,
            )

    products = get_all_serialized_products(
        search=search,
        category_id=category_id,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return jsonify(products), 200


@product_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    current_app.logger.info("GET /products/%s called", product_id)
    product = get_serialized_product_by_id(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    return jsonify(product), 200


@product_bp.route("/products", methods=["POST"])
@jwt_required()
@limiter.limit("20 per minute")
@role_required("vendor")
def create_product():
    current_app.logger.info("POST /products called by user: %s", get_jwt_identity())
    if not request.is_json:
        return jsonify({"msg": "Invalid content type"}), 400
    data = request.get_json()

    # Validate input data
    try:
        validated_data = product_schema.load(data)
    except ValidationError as err:
        return jsonify({"msg": "Validation error", "errors": err.messages}), 400

    product = create_product_with_serialization(validated_data)
    if not product:
        current_app.logger.warning("Product creation failed (possibly slug conflict): %s", data.get("slug"))
        return (
            jsonify({"message": "Error creating product (possibly slug conflict)"}),
            400,
        )
    current_app.logger.info("Product created: %s", product.get("id"))
    return jsonify({
        "message": "Product created successfully",
        **product
    }), 201


@product_bp.route("/products/<int:product_id>", methods=["PUT"])
@jwt_required()
@role_required("vendor")
def update_product(product_id):
    current_app.logger.info("PUT /products/%s called by user: %s", product_id, get_jwt_identity())
    if not request.is_json:
        return jsonify({"msg": "Invalid content type"}), 400
    data = request.get_json()

    # Validate input data
    try:
        validated_data = product_schema.load(data, partial=True)
    except ValidationError as err:
        return jsonify({"msg": "Validation error", "errors": err.messages}), 400

    product = update_product_with_serialization(product_id, validated_data)
    if not product:
        current_app.logger.warning("Product update failed: not found (id=%s)", product_id)
        return jsonify({"message": "Product not found"}), 404
    current_app.logger.info("Product updated: %s", product_id)
    return jsonify({
        "message": "Product updated successfully",
        **product
    }), 200


@product_bp.route("/products/<int:product_id>", methods=["DELETE"])
@jwt_required()
@role_required("vendor", "admin")
def delete_product(product_id):
    current_app.logger.info("DELETE /products/%s called by user: %s", product_id, get_jwt_identity())
    result = delete_product_and_return_message(product_id)
    if not result:
        current_app.logger.warning("Product delete failed: not found (id=%s)", product_id)
        return jsonify({"message": "Product not found"}), 404
    current_app.logger.info("Product deleted: %s", product_id)
    return jsonify({
        "message": "Product deleted successfully",
        **result
    }), 200


@product_bp.route("/products/<int:product_id>/approve", methods=["PATCH"])
@jwt_required()
@role_required("admin")
def approve_product(product_id):
    current_app.logger.info("PATCH /products/%s/approve called by user: %s", product_id, get_jwt_identity())
    try:
        result = product_services.approve_product_by_id(product_id)
        current_app.logger.info("Product approved: %s", product_id)
        return {"message": "Product approved"}, 200
    except ValueError as e:
        current_app.logger.warning("Product approve failed: %s (id=%s)", str(e), product_id)
        return {"message": str(e)}, 404

