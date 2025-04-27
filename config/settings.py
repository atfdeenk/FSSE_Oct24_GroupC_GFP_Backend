import os
from flask import Flask, send_from_directory, current_app
from flask_jwt_extended import JWTManager

# Define Config class properly here
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# Now continue with imports
from route.index import index_router
from route.auth_route import auth_bp
from route.product_route import product_bp
from route.product_category_routes import product_category_bp
from route.product_image_route import product_image_bp
from route.cart_route import cart_bp

import models  # noqa: F401
from instance.database import init_db



def create_app():
    app = Flask(__name__)

    # Load configuration settings
    app.config.from_object(Config)

    # Initialize JWTManager
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

    @app.route('/uploads/<path:filename>')
    def serve_uploads(filename):
        uploads_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
        return send_from_directory(uploads_path, filename)

    return app



