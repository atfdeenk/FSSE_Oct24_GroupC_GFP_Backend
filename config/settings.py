from flask import Flask
from route.index import index_router
from route.auth_route import auth_bp
from route.product_route import product_bp
from flask_jwt_extended import JWTManager  # Import the JWTManager

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

    return app
