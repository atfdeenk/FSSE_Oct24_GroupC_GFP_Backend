from instance.database import db
from shared import crono
from models.voucher import Vouchers


class Orders(db.Model):
    """Order placed by a user."""

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=crono.now)
    voucher_id = db.Column(db.Integer, db.ForeignKey("vouchers.id"), nullable=True)
    voucher = db.relationship("Vouchers")


    user = db.relationship("Users", back_populates="orders")
    order_items = db.relationship(
        "OrderItems",
        back_populates="order",
        lazy=True,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<Order {self.id} - User {self.user_id}>"
