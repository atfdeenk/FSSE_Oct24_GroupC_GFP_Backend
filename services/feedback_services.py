from repo import feedback_repo


def create_feedback(data, current_user):
    if not data:
        return None  # let route handle 400 error
    data["user_id"] = current_user["id"]
    return feedback_repo.create_feedback(data)


def get_feedback_by_product(product_id):
    return feedback_repo.get_feedback_by_product(product_id)


def get_feedback_by_user(user_id):
    return feedback_repo.get_feedback_by_user(user_id)


def get_all_feedback():
    return feedback_repo.get_all_feedback()


def delete_feedback(feedback_id, current_user):
    return feedback_repo.delete_feedback(feedback_id, current_user["id"])
