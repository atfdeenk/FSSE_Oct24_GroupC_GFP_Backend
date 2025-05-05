import os
import redis
import logging
import sys
from shared.limiter import limiter
from shared.redis_check import check_redis_connection

from flask import Flask, send_from_directory, current_app
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import models  # noqa: F401
from instance.database import init_db, db

from flask import jsonify
from werkzeug.exceptions import HTTPException
from utils.logger import setup_logger

# Import blueprints
from route.index import index_router
from route.auth_route import auth_bp
from route.product_route import product_bp
from route.product_category_routes import product_category_bp
from route.product_image_route import product_image_bp
from route.cart_route import cart_bp
from route.category_route import category_bp
from route.feedback_route import feedback_bp
from route.order_route import order_bp
from route.wishlist_route import wishlist_bp

# Import error handlers
from route.error_handlers import register_error_handlers


def create_app(config_module=None):
    """Create a Flask application instance."""
    app = Flask(__name__)

    # Configure app logger to output to console at INFO level
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    handler.setFormatter(formatter)
    if not app.logger.hasHandlers():
        app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    # Determine configuration
    config_path = config_module or os.getenv(
        "CONFIG_MODULE", "config.config.LocalConfig"
    )
    app.config.from_object(config_path)

    # 🛠️ ENABLE CORS HERE
    # CORS(app, origins=["https://bumibrew-pearl.vercel.app"], supports_credentials=True)
    CORS(app)

    # Setup extensions
    jwt = JWTManager(app)
    init_db(app)

    setup_logger(app)

    # Register error handlers
    register_error_handlers(app, jwt)

    # Setup Flask-Limiter (in-memory, no Redis)
    limiter.init_app(app)

    # Check if Redis URL is set and if Redis is reachable
    check_redis_connection(app)

    @app.errorhandler(429)
    def ratelimit_handler(e: HTTPException):
        return (
            jsonify(
                {
                    "msg": "Too many login attempts. Please wait and try again shortly.",
                    "limit": str(e.description),
                }
            ),
            429,
        )

    # Teardown after each request
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        try:
            db.session.remove()
        except Exception as e:
            # Log the error if needed (avoid print in production)
            current_app.logger.warning(f"Failed to remove DB session: {e}")

    # Register blueprints
    app.register_blueprint(index_router)
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(product_category_bp)
    app.register_blueprint(product_image_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(wishlist_bp)

    @app.route("/uploads/<path:filename>")
    def serve_uploads(filename):
        uploads_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "uploads")
        )
        return send_from_directory(uploads_path, filename)

    return app
