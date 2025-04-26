from instance.database import db


class OrderItems(db.Model):
    """Products included in an order."""

    __tablename__ = "order_items"

    id: int = db.Column(db.Integer, primary_key=True)
    order_id: int = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id: int = db.Column(
        db.Integer, db.ForeignKey("products.id"), nullable=False
    )
    quantity: int = db.Column(db.Integer, nullable=False)
    unit_price: float = db.Column(db.Numeric(10, 2), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    order = db.relationship("Orders", back_populates="order_items")
    product = db.relationship("Products", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem Order ID {self.order_id} Product ID {self.product_id}>"
