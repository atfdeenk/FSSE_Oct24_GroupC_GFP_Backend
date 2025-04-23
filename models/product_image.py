from instance.database import db


class ProductImages(db.Model):
    __tablename__ = "images"

    id = db.Column(db.Integer, primary_key=True)
    image1_url = db.Column(db.Text, nullable=True)
    image2_url = db.Column(db.Text, nullable=True)
    image3_url = db.Column(db.Text, nullable=True)

    product_id = db.Column(
        db.Integer, db.ForeignKey("products.id"), nullable=False
    )

    def __repr__(self):
        return f"<ProductImage for Product ID {self.product_id}>"
