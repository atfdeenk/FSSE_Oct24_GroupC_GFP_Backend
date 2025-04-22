from instance.database import db
from datetime import datetime
from shared import crono
import enum


class RoleType(enum.Enum):
    customer = "customer"
    vendor = "vendor"
    admin = "admin"


class Users(db.Model):
    """User model for the application."""

    __tablename__ = "users"

    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(80), unique=True, nullable=False)
    first_name: str = db.Column(db.String(80), nullable=False)
    last_name: str = db.Column(db.String(80), nullable=False)
    email: str = db.Column(db.String(120), unique=True, nullable=False)
    phone: str = db.Column(db.String(20), unique=True, nullable=False)
    password_hash: str = db.Column(db.String(512), nullable=False)
    date_of_birth: str = db.Column(db.String(10), nullable=False)
    address: str = db.Column(db.String(255), nullable=False)
    city: str = db.Column(db.String(80), nullable=False)
    state: str = db.Column(db.String(80), nullable=False)
    country: str = db.Column(db.String(80), nullable=False)
    zip_code: str = db.Column(db.String(20), nullable=False)
    image_url: str = db.Column(db.String(255), nullable=False)
    role: str = db.Column(db.Enum(RoleType), nullable=False)
    bank_account: str = db.Column(db.String(20), nullable=False)
    bank_name: str = db.Column(db.String(80), nullable=False)
    is_active: bool = db.Column(db.Boolean, default=True)
    created_at: datetime = db.Column(db.DateTime, default=crono.now)
    updated_at: datetime = db.Column(db.DateTime, default=crono.now, onupdate=crono.now)

    # Relationships
    products = db.relationship("Product", backref="vendor", lazy=True)
    categories = db.relationship("Category", backref="owner", lazy=True)
    cart = db.relationship("Cart", uselist=False, backref="user")
    orders = db.relationship("Order", back_populates="user", lazy=True)
    feedback = db.relationship("Feedback", back_populates="user", lazy=True)
    wishlist_items = db.relationship("WishlistItem", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"
