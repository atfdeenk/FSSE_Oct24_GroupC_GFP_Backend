import os
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from services import product_image_services as product_image_service
from shared.auth import role_required
from werkzeug.utils import secure_filename

product_image_bp = Blueprint("product_image_bp", __name__)

UPLOAD_FOLDER = "uploads"


@product_image_bp.route("/products/<int:product_id>/upload-image", methods=["POST"])
@role_required("vendor")
def upload_image(product_id):
    if "image" not in request.files:
        current_app.logger.warning(f"Image upload failed: No file part in request for product {product_id}.")
        return jsonify({"message": "No file part in the request"}), 400

    file = request.files["image"]

    if file.filename == "":
        current_app.logger.warning(f"Image upload failed: No selected file for product {product_id}.")
        return jsonify({"message": "No selected file"}), 400

    result = product_image_service.save_uploaded_image(product_id, file)

    if not result:
        current_app.logger.error(f"Image upload failed for product {product_id}.")
        return jsonify({"message": "Failed to upload image"}), 500

    current_app.logger.info(f"Image uploaded successfully for product {product_id}: {result['filename']}")
    return (
        jsonify(
            {
                "message": "Image uploaded successfully",
                "filename": result["filename"],
                "url": result["url"],
            }
        ),
        201,
    )


@product_image_bp.route("/products/<int:product_id>/images", methods=["POST"])
@role_required("vendor")
def create_images(product_id):
    data = request.get_json()
    current_app.logger.info(f"Creating images for product {product_id}.")
    images = product_image_service.add_images(product_id, data)
    return (
        jsonify(
            {
                "product_id": images.product_id,
                "image1_url": images.image1_url,
                "image2_url": images.image2_url,
                "image3_url": images.image3_url,
            }
        ),
        201,
    )


@product_image_bp.route("/products/<int:product_id>/images", methods=["GET"])
def get_images(product_id):
    current_app.logger.info(f"Fetching images for product {product_id}.")
    images = product_image_service.get_images(product_id)
    if not images:
        current_app.logger.warning(f"No images found for product {product_id}.")
        return jsonify({"message": "No images found"}), 404
    return (
        jsonify(
            {
                "product_id": images.product_id,
                "image1_url": images.image1_url,
                "image2_url": images.image2_url,
                "image3_url": images.image3_url,
            }
        ),
        200,
    )


@product_image_bp.route("/products/<int:product_id>/images", methods=["PUT"])
@role_required("vendor")
def update_images(product_id):
    data = request.get_json()
    current_app.logger.info(f"Updating images for product {product_id}.")
    updated = product_image_service.update_images(product_id, data)
    if not updated:
        current_app.logger.warning(f"Images not found for update on product {product_id}.")
        return jsonify({"message": "Images not found"}), 404
    return (
        jsonify(
            {
                "message": "Images updated successfully",
                "product_id": updated.product_id,
                "image1_url": updated.image1_url,
                "image2_url": updated.image2_url,
                "image3_url": updated.image3_url,
            }
        ),
        200,
    )


@product_image_bp.route("/products/<int:product_id>/images", methods=["DELETE"])
@role_required("vendor", "admin")
def delete_images(product_id):
    current_app.logger.info(f"Deleting images for product {product_id}.")
    success = product_image_service.delete_images(product_id)
    if not success:
        current_app.logger.warning(f"Images not found for deletion on product {product_id}.")
        return jsonify({"message": "Images not found"}), 404
    current_app.logger.info(f"Images deleted successfully for product {product_id}.")
    return jsonify({"message": "Images deleted successfully"}), 200
