import os
from werkzeug.security import generate_password_hash

def hash_password(password: str) -> str:
    if os.getenv("FLASK_ENV") == "development":
        return generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
    return generate_password_hash(password)  # secure default
