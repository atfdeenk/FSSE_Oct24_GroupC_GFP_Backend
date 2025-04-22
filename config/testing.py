# config/testing.py

TESTING = True
DB_HOST = "localhost"
DB_NAME = "test_db"
SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"

# Add the JWT secret key (symmetric key for HS256)
JWT_SECRET_KEY = "8493dc8a7194633818aa41f84be46e3d99fb98f86163d3bbdd35eb6ee87345e8"  
