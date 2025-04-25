from instance.database import db
from datetime import datetime
from shared import crono


class Categories(db.Model):
    """Product categories model."""

    __tablename__ = "categories"

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(120), nullable=False)
    slug: str = db.Column(db.String(120), nullable=False, unique=True)
    image_url: str = db.Column(db.Text, nullable=True)

    vendor_id: int = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    parent_id: int = db.Column(
        db.Integer, db.ForeignKey("categories.id"), nullable=True
    )

    created_at: datetime = db.Column(db.DateTime, default=crono.now)
    updated_at: datetime = db.Column(db.DateTime, default=crono.now, onupdate=crono.now)

    # Relationships
    parent = db.relationship("Categories", remote_side=[id], backref="subcategories")
    products = db.relationship(
        "ProductCategories",
        lazy=True,
        cascade="all, delete-orphan",
        passive_deletes=True,
        overlaps="products_linked,categories,product"
    )







    def __repr__(self):
        return f"<Category {self.name}>"
