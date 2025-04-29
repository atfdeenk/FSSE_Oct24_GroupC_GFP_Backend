from repo import feedback_repo
from models.user import Users  # Needed for email to user lookup


def create_feedback(data, current_user_id):
    if not data:
        return None, "Invalid data"

    user = Users.query.filter_by(id=current_user_id).first()
    if not user:
        return None, "User not found"

    # ✅ Required fields
    required_fields = ["product_id", "rating", "comment"]
    for field in required_fields:
        if field not in data:
            return None, f"Missing field: {field}"

    # ✅ Optional field: subject (validate type only if present)
    if "subject" in data and not isinstance(data["subject"], str):
        return None, "Subject must be a string"

    if not isinstance(data["rating"], int) or not (1 <= data["rating"] <= 5):
        return None, "Rating must be an integer between 1 and 5"

    if not isinstance(data["comment"], str):
        return None, "Comment must be a string"

    data["user_id"] = user.id

    try:
        feedback = feedback_repo.create_feedback(data)
    except Exception as e:
        from instance.database import db

        db.session.rollback()
        print(f"Exception creating feedback: {e}, data: {data}")
        return None, "Failed to create feedback"

    return feedback, None


def get_feedback_by_product(product_id):
    return feedback_repo.get_feedback_by_product(product_id)


def get_feedback_by_user(user_id):
    return feedback_repo.get_feedback_by_user(user_id)


# ✅ Fix here: accept page and per_page
def get_all_feedback(page=1, per_page=10):
    return feedback_repo.get_all_feedback(page=page, per_page=per_page)


def delete_feedback(feedback_id, current_user_id):
    user = Users.query.filter_by(id=current_user_id).first()
    if not user:
        return None, "User not found"
    return feedback_repo.delete_feedback(feedback_id, user.id)
