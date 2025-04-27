# config/settings.py

import os
from flask import Flask
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


def create_app(config_module=None):
    app = Flask(__name__)

    # Determine configuration
    config_path = config_module or os.getenv(
        "CONFIG_MODULE", "config.config.LocalConfig"
    )
    app.config.from_object(config_path)

    # Setup extensions
    CORS(app)
    JWTManager(app)
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

    return app
