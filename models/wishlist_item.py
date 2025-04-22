from instance.database import db
from datetime import datetime
from shared import crono


class WishlistItems(db.Model):
    """Wishlist entry saved by a user."""

    __tablename__ = "wishlist_items"

    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id: int = db.Column(
        db.Integer, db.ForeignKey("products.id"), nullable=False
    )
    vendor_id: int = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    added_at: datetime = db.Column(db.DateTime, default=crono.now)

    def __repr__(self):
        return f"<WishlistItem User {self.user_id} Product {self.product_id}>"
