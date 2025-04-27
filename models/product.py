from instance.database import db
from datetime import datetime
from shared import crono
from models.category import Categories


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
    featured: bool = db.Column(db.Boolean, default=False)
    flash_sale: bool = db.Column(db.Boolean, default=False)

    vendor_id: int = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    vendor = db.relationship(
        "Users", back_populates="products", overlaps="vendor,products"
    )

    @property
    def location(self):
        return self.vendor.city

    created_at: datetime = db.Column(db.DateTime, default=crono.now)
    updated_at: datetime = db.Column(db.DateTime, default=crono.now, onupdate=crono.now)

    # Relationships
    # For ProductCategories join table
    categories = db.relationship(
        "ProductCategories",
        lazy=True,
        cascade="all, delete-orphan",
        passive_deletes=True,
        overlaps="categories_linked,products_linked,category",
    )

    categories_linked = db.relationship(
        "Categories",
        secondary="product_categories",
        backref=db.backref(
            "products_linked",
            lazy="joined",
            overlaps="categories,categories_linked,product",
        ),
        lazy="joined",
        overlaps="categories,product,products",
    )

    images = db.relationship("ProductImages", backref="product", lazy=True)
    order_items = db.relationship("OrderItems", back_populates="product", lazy=True)
    cart_items = db.relationship("CartItems", backref="product", lazy=True)
    feedback = db.relationship("Feedbacks", backref="product", lazy=True)
    wishlist_items = db.relationship("WishlistItems", backref="product", lazy=True)

    def __repr__(self):
        return f"<Product {self.name}>"


# This alias exists ONLY to satisfy `db.relationship("Product")`
Product = Products
