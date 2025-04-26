from instance.database import db
from models.feedback import Feedbacks


def create_feedback(data):
    feedback = Feedbacks(**data)
    db.session.add(feedback)
    db.session.commit()
    return feedback


def get_feedback_by_product(product_id):
    return Feedbacks.query.filter_by(product_id=product_id).all()


def get_feedback_by_user(user_id):
    return Feedbacks.query.filter_by(user_id=user_id).all()


def get_all_feedback(page=1, per_page=10):
    return Feedbacks.query.paginate(page=page, per_page=per_page, error_out=False).items


def delete_feedback(feedback_id, user_id):
    feedback = Feedbacks.query.get(feedback_id)
    if not feedback:
        return None, "Feedback not found"
    if feedback.user_id != user_id:
        return None, "Unauthorized"
    db.session.delete(feedback)
    db.session.commit()
    return feedback, None
