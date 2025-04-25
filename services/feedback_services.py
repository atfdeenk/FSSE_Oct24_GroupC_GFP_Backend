from repo import feedback_repo
from models.user import Users


def create_feedback(data, current_user_email):
    if not data:
        return None  # let route handle 400 error

    user = Users.query.filter_by(email=current_user_email).first()
    if not user:
        raise Exception("User not found")
    data["user_id"] = user.id
    return feedback_repo.create_feedback(data)


def get_feedback_by_product(product_id):
    return feedback_repo.get_feedback_by_product(product_id)


def get_feedback_by_user(user_id):
    return feedback_repo.get_feedback_by_user(user_id)


def get_all_feedback():
    return feedback_repo.get_all_feedback()


def delete_feedback(feedback_id, current_user_email):
    user = Users.query.filter_by(email=current_user_email).first()
    if not user:
        raise Exception("User not found")
    return feedback_repo.delete_feedback(feedback_id, user.id)
