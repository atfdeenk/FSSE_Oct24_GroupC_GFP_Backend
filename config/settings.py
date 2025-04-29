# config/settings.py

import os
from flask import Flask, send_from_directory, current_app
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import models  # noqa: F401
from instance.database import init_db

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


def create_app(config_module="Config.testing"):
    app = Flask(__name__)

    # Determine configuration
    config_path = config_module or os.getenv(
        "CONFIG_MODULE", "config.config.LocalConfig"
    )
    app.config.from_object(config_module)

    # 🛠️ ENABLE CORS HERE
    # CORS(app, origins=["https://bumibrew-pearl.vercel.app"], supports_credentials=True)
    CORS(app)

    # Setup extensions
    JWTManager(app)
    CORS(app, supports_credentials=True)
    init_db(app)

    # Teardown after each request
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        from instance.database import db

        db.session.remove()

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
