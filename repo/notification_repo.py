from models.notification import Notification
from instance.database import db


class NotificationRepo:
    @staticmethod
    def get_unread_notifications(user_id):
        return (
            Notification.query.filter_by(user_id=user_id, is_read=False)
            .order_by(Notification.created_at.desc())
            .all()
        )

    @staticmethod
    def mark_notification_as_read(notification_id):
        notification = Notification.query.get(notification_id)
        if notification:
            notification.is_read = True
            try:
                db.session.commit()
                return notification
            except Exception as e:
                db.session.rollback()
                return None
        return None
