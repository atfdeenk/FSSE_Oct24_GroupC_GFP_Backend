from flask import Flask
from route.index import index_router

import models  # noqa: F401
from instance.database import init_db


def create_app(config_module="config.local"):
    app = Flask(__name__)

    # Load configuration settings
    app.config.from_object(config_module)
    init_db(app)

    # Register routes
    app.register_blueprint(index_router)

    return app
