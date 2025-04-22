from flask import Blueprint, request, jsonify
from repo import product_repo

product_bp = Blueprint('product_bp', __name__)

@product_bp.route("/products", methods=["GET"])
def get_all_products():
    products = product_repo.get_all_products()
    return jsonify([p.__dict__ for p in products]), 200

@product_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = product_repo.get_product_by_id(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    return jsonify(product.__dict__), 200

@product_bp.route("/products", methods=["POST"])
def create_product():
    data = request.get_json()
    product = product_repo.create_product(data)
    if not product:
        return jsonify({"message": "Error creating product (possibly slug conflict)"}), 400
    return jsonify(product.__dict__), 201

@product_bp.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.get_json()
    product = product_repo.update_product(product_id, data)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    return jsonify(product.__dict__), 200

@product_bp.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = product_repo.delete_product(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404
    return jsonify({"message": "Product deleted"}), 200
