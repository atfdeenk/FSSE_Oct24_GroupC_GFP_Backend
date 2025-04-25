from models.user import User
from models.product import Product
from instance.database import db


def create_test_user(app):
    """Create and return a test user."""
    with app.app_context():
        user = User(email="testuser@example.com", password="password")
        db.session.add(user)
        db.session.commit()
        return user


def create_test_product(app):
    """Create and return a test product."""
    with app.app_context():
        product = Product(
            name="Test Product", description="Test Description", price=10.0
        )
        db.session.add(product)
        db.session.commit()
        return product
