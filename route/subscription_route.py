from flask import Blueprint, request, jsonify
from services.subscription_services import SubscriptionService

subscription_bp = Blueprint("subscription", __name__)


@subscription_bp.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json()
    if not data or "email" not in data:
        return jsonify({"error": "Email is required"}), 400

    email = data["email"]
    try:
        SubscriptionService.subscribe(email)
        return jsonify({"message": "Subscription successful. Welcome email sent."}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "Failed to send welcome email."}), 500
