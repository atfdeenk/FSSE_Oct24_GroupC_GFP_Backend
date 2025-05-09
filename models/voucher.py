from instance.database import db
from shared import crono

class Vouchers(db.Model):
    __tablename__ = "vouchers"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_percent = db.Column(db.Float, nullable=True)  # optional: 10 for 10%
    discount_amount = db.Column(db.Numeric(10, 2), nullable=True)  # optional: fixed
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=crono.now)

    def __repr__(self):
        return f"<Voucher {self.code}>"
