import logging

def setup_logger(app):
    # Set the base logging level
    app.logger.setLevel(logging.INFO)

    # Avoid duplicate handlers during reloads (e.g., with Flask dev server)
    if app.logger.hasHandlers():
        return

    # Stream handler (console)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    # Log format
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    handler.setFormatter(formatter)

    # Add to Flask app logger
    app.logger.addHandler(handler)
