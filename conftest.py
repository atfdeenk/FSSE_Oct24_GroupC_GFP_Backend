import pytest
import random
import string
from config.settings import create_app
from instance.database import db
from flask_jwt_extended import create_access_token
from models.user import Users
from models.product import Products
from models.product_category import ProductCategories
from models.category import Categories


def random_string(length=6):
    """Generate a random string for unique test data."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


@pytest.fixture(scope="function")
def app():
    """Create a Flask application instance for testing."""
    app = create_app("config.testing")

    # Import all models to ensure SQLAlchemy relationships are resolvable
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

        # Generate random suffix to prevent UNIQUE constraint violations
        suffix = random_string()

        # Seed vendor user
        vendor = Users(
            username=f"vendoruser_{suffix}",
            first_name="Test",
            last_name="Vendor",
            email=f"vendor_{suffix}@mail.com",
            phone=f"08123{random.randint(10000, 99999)}",
            password_hash="test",
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
            is_active=True,
        )

        # Seed customer user
        customer = Users(
            username=f"customeruser_{suffix}",
            first_name="Test",
            last_name="Customer",
            email=f"customer_{suffix}@mail.com",
            phone=f"08987{random.randint(10000, 99999)}",
            password_hash="test",
            date_of_birth="1992-05-05",
            address="Another Street 456",
            city="Bandung",
            state="West Java",
            country="Indonesia",
            zip_code="54321",
            image_url="https://example.com/customer.png",
            role="customer",
            bank_account="9876543210",
            bank_name="BCA",
            is_active=True,
        )

        # Seed admin user
        admin = Users(
            username=f"adminuser_{suffix}",
            first_name="Admin",
            last_name="User",
            email=f"admin_{suffix}@mail.com",
            phone=f"08765{random.randint(10000, 99999)}",
            password_hash="test",
            date_of_birth="1985-09-09",
            address="Admin Street 789",
            city="Surabaya",
            state="East Java",
            country="Indonesia",
            zip_code="67890",
            image_url="https://example.com/admin.png",
            role="admin",
            bank_account="1234567890",
            bank_name="BNI",
            is_active=True,
        )

        db.session.add_all([vendor, customer, admin])
        db.session.commit()

        # Make user IDs available for other fixtures
        app.test_vendor_id = vendor.id
        app.test_customer_id = customer.id
        app.test_admin_id = admin.id

        category = Categories(
            name=f"Test Category {suffix}",
            slug=f"test-category-{suffix}",
            vendor_id=vendor.id,
        )
        db.session.add(category)
        db.session.commit()

        app.test_category_id = category.id

        yield

        db.session.remove()  # Close and remove session to avoid locked DB
        db.drop_all()


@pytest.fixture
def client(app, init_db):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def vendor_token(app):
    with app.app_context():
        return create_access_token(
            identity=str(app.test_vendor_id), additional_claims={"role": "vendor"}
        )


@pytest.fixture
def customer_token(app):
    with app.app_context():
        return create_access_token(
            identity=str(app.test_customer_id), additional_claims={"role": "customer"}
        )


@pytest.fixture
def admin_token(app):
    with app.app_context():
        return create_access_token(
            identity=str(app.test_admin_id), additional_claims={"role": "admin"}
        )


@pytest.fixture
def seed_product(app):
    with app.app_context():
        product = Products(
            id=1,
            name="Test Coffee",
            slug="test-coffee",
            description="Test product description",
            currency="IDR",
            price=85000,
            stock_quantity=10,
            unit_quantity="250g",
            image_url="http://example.com/test.jpg",
            featured=False,
            flash_sale=False,
            vendor_id=app.test_vendor_id,
            is_approved=True,
        )
        db.session.add(product)

        pc = ProductCategories(product_id=1, category_id=app.test_category_id)
        db.session.add(pc)

        db.session.commit()
        yield product


@pytest.fixture
def new_user(app):
    with app.app_context():
        suffix = "newuser"
        user = Users(
            username=f"testuser_{suffix}",
            first_name="Test",
            last_name="User",
            email=f"testuser_{suffix}@mail.com",
            phone="08123456789",
            password_hash="test",
            date_of_birth="1990-01-01",
            address="Test Address",
            city="Test City",
            state="Test State",
            country="Test Country",
            zip_code="12345",
            image_url="https://example.com/user.png",
            role="customer",
            bank_account="1234567890",
            bank_name="Test Bank",
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()
        yield user
