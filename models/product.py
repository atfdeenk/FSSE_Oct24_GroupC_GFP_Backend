from instance.database import db
from datetime import datetime
from shared import crono


class Products(db.Model):
    """Product model representing items listed by vendors."""

    __tablename__ = "products"

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(120), nullable=False)
    slug: str = db.Column(db.String(120), nullable=False, unique=True)
    description: str = db.Column(db.Text, nullable=False)

    currency: str = db.Column(db.String(10), nullable=False, default="IDR")
    price: float = db.Column(db.Numeric(10, 2), nullable=False)
    discount_percentage: int = db.Column(db.Integer, default=0)

    stock_quantity: int = db.Column(db.Integer, nullable=False)
    unit_quantity: str = db.Column(db.String(50), nullable=False)

    image_url: str = db.Column(db.String(255), nullable=True)
    location: str = db.Column(db.String(120), nullable=True)
    featured: bool = db.Column(db.Boolean, default=False)
    flash_sale: bool = db.Column(db.Boolean, default=False)

    vendor_id: int = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    created_at: datetime = db.Column(db.DateTime, default=crono.now)
    updated_at: datetime = db.Column(db.DateTime, default=crono.now, onupdate=crono.now)

    # Relationships
    categories = db.relationship("ProductCategory", backref="product", lazy=True)
    images = db.relationship("ProductImage", backref="product", lazy=True)
    order_items = db.relationship("OrderItem", backref="product", lazy=True)
    cart_items = db.relationship("CartItem", backref="product", lazy=True)
    feedback = db.relationship("Feedback", backref="product", lazy=True)
    wishlist_items = db.relationship("WishlistItem", backref="product", lazy=True)

    def __repr__(self):
        return f"<Product {self.name}>"
