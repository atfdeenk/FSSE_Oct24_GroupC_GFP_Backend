# This file is part of the Flask-Email-Service project on Newsletter Subscription.
import os


def init_mail_config(app):
    """Initialize email configuration for Flask-Mail."""
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv(
        "MAIL_DEFAULT_SENDER", app.config["MAIL_USERNAME"]
    )
    # Debug logging for mail config (avoid logging passwords)
    import logging

    logging.info(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
    logging.info(f"MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")
