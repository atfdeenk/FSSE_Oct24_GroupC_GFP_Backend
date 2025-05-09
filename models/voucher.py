from instance.database import db
from shared import crono

class Vouchers(db.Model):
    __tablename__ = "vouchers"

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_percent = db.Column(db.Float, nullable=True)
    discount_amount = db.Column(db.Numeric(10, 2), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=crono.now)

    vendor = db.relationship("Users", backref="vouchers")  # ✅ add this here

    def __repr__(self):
        return f"<Voucher {self.code}>"
