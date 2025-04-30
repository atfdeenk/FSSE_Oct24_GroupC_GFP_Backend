# config/testing.py
import os

# TESTING = True
# DB_HOST = "localhost"
# DB_NAME = "test_db"
# SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"

# # Add the JWT secret key (symmetric key for HS256)
# JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "testing-secret-key")

# import os


class TestingConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "testing-secret-key")
