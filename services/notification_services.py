from repo.notification_repo import NotificationRepo


class NotificationService:
    @staticmethod
    def get_unread_notifications(user_id):
        return NotificationRepo.get_unread_notifications(user_id)

    @staticmethod
    def mark_notification_as_read(notification_id):
        return NotificationRepo.mark_notification_as_read(notification_id)
