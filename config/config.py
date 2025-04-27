import os


class LocalConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', 5432)}/{os.getenv('DB_NAME')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "testing-secret-key")

    # Reduce pool size and max overflow to strictly limit simultaneous connections
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 1,
        "max_overflow": 0,
        "pool_timeout": 30,
        "pool_recycle": 1800,
    }
