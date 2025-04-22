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

    def __repr__(self):
        return f"<OrderItem Order ID {self.order_id} Product ID {self.product_id}>"
