from instance.database import db
from datetime import datetime
from shared import crono


class Feedbacks(db.Model):
    """Review and rating given by a user to a product."""

    __tablename__ = "feedback"

    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id: int = db.Column(
        db.Integer, db.ForeignKey("products.id"), nullable=False
    )
    rating: int = db.Column(db.Integer, nullable=False)
    comment: str = db.Column(db.String(255), nullable=True)
    created_at: datetime = db.Column(db.DateTime, default=crono.now)

    user = db.relationship("Users", back_populates="feedback")

    def __repr__(self):
        return f"<Feedback User {self.user_id} Product {self.product_id}>"
