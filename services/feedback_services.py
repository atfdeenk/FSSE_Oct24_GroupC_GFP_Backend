from repo import feedback_repo
from models.user import Users  # Needed for email to user lookup


def create_feedback(data, current_user_id):
    if not data:
        return None, "Invalid data"  # let route handle 400 error

    user = Users.query.filter_by(id=current_user_id).first()
    if not user:
        return None, "User not found"

    data["user_id"] = user.id
    feedback = feedback_repo.create_feedback(data)
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
