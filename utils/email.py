from flask_mail import Message
from config.settings import mail  # pastikan Flask-Mail diinisialisasi


import logging


def send_welcome_email(email):
    subject = "Welcome to BumiBrew!"
    body = "Thank you for subscribing to our newsletter. Stay tuned for new products and special promos!"

    # Explicitly set sender from mail.default_sender or fallback to MAIL_DEFAULT_SENDER env var
    sender = getattr(mail, "default_sender", None)
    if not sender:
        import os

        sender = os.getenv("MAIL_DEFAULT_SENDER", "noreply@bumibrew.com")

    msg = Message(subject=subject, sender=sender, recipients=[email], body=body)
    try:
        mail.send(msg)
        logging.info(f"Welcome email sent to {email}")
    except Exception as e:
        logging.error(f"Failed to send welcome email to {email}: {e}")
        raise e
