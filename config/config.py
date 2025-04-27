# config/config.py

import os


class BaseConfig:
    """Base configuration shared across environments."""

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default-super-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600)
    )  # 1 hour default
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 5,  # persistent DB connections
        "max_overflow": 10,  # extra temporary connections
        "pool_timeout": 30,  # 30s wait before timeout
        "pool_recycle": 1800,  # recycle connections every 30 mins
        "pool_pre_ping": True,  # check if connection is alive before using it
    }


class LocalConfig(BaseConfig):
    """Configuration for local development."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', 5432)}/{os.getenv('DB_NAME')}",
    )
    FLASK_ENV = "development"


class ProductionConfig(BaseConfig):
    """Configuration for production deployment."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  # Must be fully provided
    FLASK_ENV = "production"
