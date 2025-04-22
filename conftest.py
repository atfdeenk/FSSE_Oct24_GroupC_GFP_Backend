import pytest
from config.settings import create_app
from instance.database import db  # Correct import for db

@pytest.fixture(scope="function")
def app():
    """Create a Flask application instance for testing."""
    app = create_app("config.testing")

    # ✅ Import all models to ensure SQLAlchemy relationships are resolvable
    import models.product
    import models.product_category
    import models.user
    import models.category
    import models.cart
    import models.cart_item
    import models.order
    import models.order_item
    import models.feedback
    import models.product_image
    import models.wishlist_item

    return app

@pytest.fixture(scope="function")
def init_db(app):
    """Create the database tables before tests and drop them afterward."""
    with app.app_context():
        db.create_all()  # Create tables in test database
        yield
        db.drop_all()  # Clean up after test

@pytest.fixture
def client(app, init_db):
    """Create a test client for the Flask application."""
    return app.test_client()
