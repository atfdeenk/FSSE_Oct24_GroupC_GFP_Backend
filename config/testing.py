# config/testing.py
import os

TESTING = True
DB_HOST = "localhost"
DB_NAME = "test_db"
SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
RATELIMIT_ENABLED = False


# Add the JWT secret key (symmetric key for HS256)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "testing-secret-key")
