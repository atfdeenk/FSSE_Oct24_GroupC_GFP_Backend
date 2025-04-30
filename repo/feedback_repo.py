from instance.database import db
from models.feedback import Feedbacks


def create_feedback(data):
    feedback = Feedbacks(**data)
    db.session.add(feedback)
    db.session.flush()  # Assign id before returning
    return feedback


def get_feedback_by_product(product_id):
    return Feedbacks.query.filter_by(product_id=product_id).all()


def get_feedback_by_user(user_id):
    return Feedbacks.query.filter_by(user_id=user_id).all()


def get_all_feedback(page=1, per_page=10):
    return Feedbacks.query.paginate(page=page, per_page=per_page, error_out=False).items


def delete_feedback(feedback_id, user_id):
    feedback = db.session.get(Feedbacks, feedback_id)
    if not feedback:
        return None, "Feedback not found"
    if feedback.user_id != user_id:
        return None, "Unauthorized"
    db.session.delete(feedback)
    return feedback, None
