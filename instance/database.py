from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db = SQLAlchemy()
migrate = Migrate()


def init_db(app):
    engine_options = app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {})
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], **engine_options)
    # Bind the engine to the SQLAlchemy db object
    db.engine = engine

    db.init_app(app)
    migrate.init_app(app, db)
    # Initialize the database and migration engine
