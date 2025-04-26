from repo import feedback_repo
from models.user import Users  # Needed for email to user lookup


from models.product import Products


def create_feedback(data, current_user_email):
    if not data:
        return None  # let route handle 400 error

    user = Users.query.filter_by(email=current_user_email).first()
    if not user:
        return None

    # Validate required fields
    if "product_id" not in data or "rating" not in data:
        return None

    # Check if product exists
    product = Products.query.filter_by(id=data["product_id"]).first()
    if not product:
        return None

    data["user_id"] = user.id
    return feedback_repo.create_feedback(data)


def get_feedback_by_product(product_id):
    return feedback_repo.get_feedback_by_product(product_id)


def get_feedback_by_user(user_id):
    return feedback_repo.get_feedback_by_user(user_id)


# ✅ Fix here: accept page and per_page
def get_all_feedback(page=1, per_page=10):
    return feedback_repo.get_all_feedback(page=page, per_page=per_page)


def delete_feedback(feedback_id, current_user_email, current_user_role):
    user = Users.query.filter_by(email=current_user_email).first()
    if not user:
        return None, "User not found"

    if current_user_role == "admin":
        # Admin can delete any feedback
        feedback = feedback_repo.get_feedback_by_id(feedback_id)
        if not feedback:
            return None, "Feedback not found"
        feedback_repo.delete_feedback_by_instance(feedback)
        return feedback, None
    else:
        # Non-admin can delete only their own feedback
        return feedback_repo.delete_feedback(feedback_id, user.id)
