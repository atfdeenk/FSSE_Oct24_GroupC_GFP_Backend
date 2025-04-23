from flask import Blueprint, request, jsonify
from services import product_image_services as product_image_service
from shared.auth import role_required

product_image_bp = Blueprint("product_image_bp", __name__)

@product_image_bp.route("/products/<int:product_id>/images", methods=["POST"])
@role_required("vendor")
def create_images(product_id):
    data = request.get_json()
    images = product_image_service.add_images(product_id, data)
    return jsonify({
        "product_id": images.product_id,
        "image1_url": images.image1_url,
        "image2_url": images.image2_url,
        "image3_url": images.image3_url,
    }), 201

@product_image_bp.route("/products/<int:product_id>/images", methods=["GET"])
def get_images(product_id):
    images = product_image_service.get_images(product_id)
    if not images:
        return jsonify({"message": "No images found"}), 404
    return jsonify({
        "product_id": images.product_id,
        "image1_url": images.image1_url,
        "image2_url": images.image2_url,
        "image3_url": images.image3_url,
    }), 200

@product_image_bp.route("/products/<int:product_id>/images", methods=["PUT"])
@role_required("vendor")
def update_images(product_id):
    data = request.get_json()
    updated = product_image_service.update_images(product_id, data)
    if not updated:
        return jsonify({"message": "Images not found"}), 404
    return jsonify({
        "product_id": updated.product_id,
        "image1_url": updated.image1_url,
        "image2_url": updated.image2_url,
        "image3_url": updated.image3_url,
    }), 200

@product_image_bp.route("/products/<int:product_id>/images", methods=["DELETE"])
@role_required("vendor")
def delete_images(product_id):
    success = product_image_service.delete_images(product_id)
    if not success:
        return jsonify({"message": "Images not found"}), 404
    return jsonify({"message": "Images deleted"}), 200

