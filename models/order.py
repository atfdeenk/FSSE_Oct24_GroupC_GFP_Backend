from instance.database import db
from datetime import datetime
from shared import crono


class Orders(db.Model):
    """Order placed by a user."""

    __tablename__ = "orders"

    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    total_amount: float = db.Column(db.Numeric(10, 2), nullable=False)
    status: str = db.Column(db.String(50), nullable=False)
    created_at: datetime = db.Column(db.DateTime, default=crono.now)

    user = db.relationship("Users", back_populates="orders")
    order_items = db.relationship("OrderItems", backref="order", lazy=True)

    def __repr__(self):
        return f"<Order {self.id} - User {self.user_id}>"
