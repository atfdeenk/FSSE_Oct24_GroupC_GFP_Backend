from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import feedback_services
from models.user import Users

feedback_bp = Blueprint("feedback_bp", __name__)


@feedback_bp.route("/feedback", methods=["POST"])
@jwt_required()
def create_feedback():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    current_app.logger.info(f"User {current_user_id} submitting feedback: {data}")
    if not data:
        current_app.logger.warning(f"User {current_user_id} submitted invalid feedback request.")
        return jsonify({"msg": "Invalid request"}), 400

    feedback, error = feedback_services.create_feedback(data, current_user_id)
    if error:
        current_app.logger.error(f"Create feedback error: {error}, data: {data}")
        return jsonify({"msg": error}), 400
    if feedback is None:
        current_app.logger.warning(f"User {current_user_id} failed to create feedback.")
        return jsonify({"msg": "Failed to create feedback"}), 400
    current_app.logger.info(f"Feedback {feedback.id} submitted successfully by user {current_user_id}.")
    return (
        jsonify(
            {
                "msg": "Feedback submitted successfully",
                "feedback": {
                    "id": feedback.id,
                    "user_id": feedback.user_id,
                    "product_id": feedback.product_id,
                    "rating": feedback.rating,
                    "comment": feedback.comment,
                    "created_at": feedback.created_at.isoformat(),
                },
            }
        ),
        201,
    )


@feedback_bp.route("/feedback/product/<int:product_id>", methods=["GET"])
def get_feedback_by_product(product_id):
    current_app.logger.info(f"Fetching feedback for product {product_id}.")
    feedback_list = feedback_services.get_feedback_by_product(product_id)
    return (
        jsonify(
            {
                "msg": "Feedback retrieved successfully",
                "count": len(feedback_list),
                "feedback": [
                    {
                        "id": fb.id,
                        "user_id": fb.user_id,
                        "product_id": fb.product_id,
                        "rating": fb.rating,
                        "comment": fb.comment,
                        "created_at": fb.created_at.isoformat(),
                    }
                    for fb in feedback_list
                ],
            }
        ),
        200,
    )


@feedback_bp.route("/feedback/user/<int:user_id>", methods=["GET"])
@jwt_required()
def get_feedback_by_user(user_id):
    current_user_id = get_jwt_identity()
    current_app.logger.info(f"User {current_user_id} requesting feedback for user {user_id}.")
    user = Users.query.filter_by(id=current_user_id).first()

    if not user or user.id != user_id:
        current_app.logger.warning(f"Unauthorized feedback access attempt by user {current_user_id} for user {user_id}.")
        return jsonify({"msg": "Unauthorized"}), 403

    feedback_list = feedback_services.get_feedback_by_user(user_id)
    return (
        jsonify(
            {
                "msg": "Feedback retrieved successfully",
                "count": len(feedback_list),
                "feedback": [
                    {
                        "id": fb.id,
                        "product_id": fb.product_id,
                        "rating": fb.rating,
                        "comment": fb.comment,
                        "created_at": fb.created_at.isoformat(),
                    }
                    for fb in feedback_list
                ],
            }
        ),
        200,
    )


@feedback_bp.route("/feedback", methods=["GET"])
def get_all_feedback():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    current_app.logger.info(f"Fetching all feedback (page {page}, per_page {per_page}).")

    feedback_list = feedback_services.get_all_feedback(page=page, per_page=per_page)
    return (
        jsonify(
            {
                "msg": "Feedback retrieved successfully",
                "count": len(feedback_list),
                "feedback": [
                    {
                        "id": fb.id,
                        "user_id": fb.user_id,
                        "product_id": fb.product_id,
                        "rating": fb.rating,
                        "comment": fb.comment,
                        "created_at": fb.created_at.isoformat(),
                    }
                    for fb in feedback_list
                ],
            }
        ),
        200,
    )


@feedback_bp.route("/feedback/<int:feedback_id>", methods=["DELETE"])
@jwt_required()
def delete_feedback(feedback_id):
    current_user_id = get_jwt_identity()
    current_app.logger.info(f"User {current_user_id} attempting to delete feedback {feedback_id}.")
    feedback, error = feedback_services.delete_feedback(feedback_id, current_user_id)
    if error:
        current_app.logger.warning(f"Failed to delete feedback {feedback_id} by user {current_user_id}: {error}")
        return jsonify({"msg": error}), 403 if error == "Unauthorized" else 404
    current_app.logger.info(f"Feedback {feedback_id} deleted successfully by user {current_user_id}.")
    return jsonify({"msg": "Feedback deleted successfully"}), 200
