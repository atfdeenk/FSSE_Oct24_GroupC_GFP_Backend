from flask import Flask, send_from_directory, current_app
import os

# Import routes
from route.index import index_router
from route.auth_route import auth_bp
from route.product_route import product_bp
from route.product_category_routes import product_category_bp
from route.product_image_route import product_image_bp
from route.cart_route import cart_bp
from route.category_route import category_bp
from route.feedback_route import feedback_bp
from flask_jwt_extended import JWTManager  # Import the JWTManager
from flask import send_from_directory


import models  # noqa: F401
from instance.database import init_db


def create_app(config_module="config.testing"):
    app = Flask(__name__)

    # Load configuration settings
    app.config.from_object(config_module)

    # Initialize JWTManager here
    jwt = JWTManager(app)

    # Initialize the database
    init_db(app)

    # Register routes
    app.register_blueprint(index_router)
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(product_category_bp)
    app.register_blueprint(product_image_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(feedback_bp)

    @app.route('/uploads/<path:filename>')
    def serve_uploads(filename):
        uploads_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
        return send_from_directory(uploads_path, filename)

    return app


