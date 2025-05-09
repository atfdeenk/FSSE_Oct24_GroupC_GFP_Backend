from utils.email import send_welcome_email


class SubscriptionService:
    @staticmethod
    def subscribe(email: str):
        if not email:
            raise ValueError("Email is required")
        # Additional email validation can be added here
        try:
            send_welcome_email(email)
            return True
        except Exception as e:
            raise e
