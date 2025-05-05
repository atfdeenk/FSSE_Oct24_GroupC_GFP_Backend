from flask import Blueprint, request, jsonify, current_app
from services import product_category_services as product_category_service
from shared.auth import role_required

product_category_bp = Blueprint("product_category_bp", __name__)


@product_category_bp.route("/products/<int:product_id>/categories", methods=["POST"])
@role_required("vendor")
def add_category(product_id):
    data = request.get_json()
    category_id = data.get("category_id")
    current_app.logger.info(f"Vendor attempting to assign category {category_id} to product {product_id}.")
    if not category_id:
        current_app.logger.warning("Category assignment failed: category_id required.")
        return jsonify({"message": "category_id required"}), 400

    relation = product_category_service.assign_category(product_id, category_id)
    if not relation:
        current_app.logger.warning(f"Category assignment failed for product {product_id} and category {category_id}.")
        return jsonify({"message": "Category already assigned or failed"}), 400

    current_app.logger.info(f"Category {category_id} assigned to product {product_id} successfully.")
    return (
        jsonify(
            {
                "message": "Category assigned successfully",
                "product_id": relation.product_id,
                "category_id": relation.category_id,
            }
        ),
        201,
    )


@product_category_bp.route("/products/<int:product_id>/categories", methods=["GET"])
@role_required("customer", "vendor")
def get_categories(product_id):
    current_app.logger.info(f"Fetching categories for product {product_id}.")
    relations = product_category_service.get_product_categories(product_id)
    return (
        jsonify(
            {
                "message": "Categories fetched successfully",
                "categories": [
                    {"product_id": r.product_id, "category_id": r.category_id}
                    for r in relations
                ],
            }
        ),
        200,
    )


@product_category_bp.route(
    "/products/<int:product_id>/categories/<int:category_id>", methods=["DELETE"]
)
@role_required("vendor")
def delete_category(product_id, category_id):
    current_app.logger.info(f"Vendor attempting to remove category {category_id} from product {product_id}.")
    success = product_category_service.remove_category(product_id, category_id)
    if not success:
        current_app.logger.warning(f"Category removal failed: relation not found for product {product_id} and category {category_id}.")
        return jsonify({"message": "Relation not found"}), 404
    current_app.logger.info(f"Category {category_id} removed from product {product_id} successfully.")
    return jsonify({"message": "Category removed"}), 200
