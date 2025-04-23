import pytest
from config.settings import create_app
from instance.database import db
from flask_jwt_extended import create_access_token
from models.user import Users

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
    """Create the database tables and seed test data."""
    with app.app_context():
        db.create_all()

        # ✅ Seed test vendor user
        vendor = Users(
            id=1,
            username="vendoruser",
            first_name="Test",
            last_name="Vendor",
            email="vendor@mail.com",
            phone="081234567890",
            password_hash="test",  # acceptable for test
            date_of_birth="1990-01-01",
            address="Test Street 123",
            city="Jakarta",
            state="DKI Jakarta",
            country="Indonesia",
            zip_code="12345",
            image_url="https://example.com/image.png",
            role="vendor",
            bank_account="1234567890",
            bank_name="BNI",
            is_active=True
        )
        db.session.add(vendor)

        # ✅ Seed category with ID 1
        from models.category import Categories
        category = Categories(
            id=1,
            name="Test Category",
            slug="test-category",
            vendor_id=1  # Required field to pass NOT NULL constraint
        )
        db.session.add(category)

        db.session.commit()
        yield
        db.drop_all()

@pytest.fixture
def client(app, init_db):
    """Create a test client for the Flask application."""
    return app.test_client()

@pytest.fixture
def vendor_token(app):
    with app.app_context():
        return create_access_token(identity=str(1), additional_claims={"role": "vendor"})

@pytest.fixture
def user_token(app):
    with app.app_context():
        return create_access_token(identity=str(2), additional_claims={"role": "user"})

@pytest.fixture
def admin_token(app):
    with app.app_context():
        return create_access_token(identity=str(3), additional_claims={"role": "admin"})
