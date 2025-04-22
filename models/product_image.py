from instance.database import db


class ProductImages(db.Model):
    """Additional images for a product."""

    __tablename__ = "images"

    id: int = db.Column(db.Integer, primary_key=True)
    image1_url: str = db.Column(db.Text, nullable=True)
    image1_ur2: str = db.Column(db.Text, nullable=True)
    image1_ur3: str = db.Column(db.Text, nullable=True)

    product_id: int = db.Column(
        db.Integer, db.ForeignKey("products.id"), nullable=False
    )

    def __repr__(self):
        return f"<ProductImage for Product ID {self.product_id}>"
