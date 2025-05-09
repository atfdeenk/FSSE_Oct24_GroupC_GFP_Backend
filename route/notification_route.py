from flask import Blueprint, jsonify, request
from services.notification_services import NotificationService

notification_bp = Blueprint("notification_bp", __name__)


# Placeholder function to get current user id
def get_current_user_id():
    # TODO: Replace with actual user authentication logic
    # For now, assume user_id is passed as a query param for testing
    user_id = request.args.get("user_id", type=int)
    return user_id


@notification_bp.route("/notifications", methods=["GET"])
def get_notifications():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    notifications = NotificationService.get_unread_notifications(user_id)
    result = []
    for n in notifications:
        result.append(
            {
                "id": n.id,
                "user_id": n.user_id,
                "message": n.message,
                "link": n.link,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
        )
    return jsonify(result), 200


@notification_bp.route("/notifications/<int:id>/read", methods=["PATCH"])
def mark_notification_read(id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    notification = NotificationService.mark_notification_as_read(id)
    if notification is None:
        return jsonify({"error": "Notification not found"}), 404
    if notification.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"message": "Notification marked as read"}), 200
