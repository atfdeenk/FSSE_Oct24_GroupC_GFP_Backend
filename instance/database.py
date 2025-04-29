from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine


class CustomSQLAlchemy(SQLAlchemy):
    def create_engine(self, *args, **kwargs):
        app = self.get_app()
        engine_options = app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {})
        kwargs.update(engine_options)
        return create_engine(*args, **kwargs)


db = CustomSQLAlchemy()
migrate = Migrate()


def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db)
    print(
        "[INFO] SQLAlchemy engine options:", app.config.get("SQLALCHEMY_ENGINE_OPTIONS")
    )
    # Initialize the database and migration engine
