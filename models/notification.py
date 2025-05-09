from instance.database import db
from shared import crono


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), nullable=True)  # URL ke detail
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=crono.now)
