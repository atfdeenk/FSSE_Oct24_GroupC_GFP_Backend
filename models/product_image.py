from instance.database import db


class ProductImages(db.Model):
    __tablename__ = "images"

    id = db.Column(db.Integer, primary_key=True)
    image1_url = db.Column(db.Text, nullable=True)
    image2_url = db.Column(db.Text, nullable=True)  # ✅ must exist
    image3_url = db.Column(db.Text, nullable=True)  # ✅ must exist
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
