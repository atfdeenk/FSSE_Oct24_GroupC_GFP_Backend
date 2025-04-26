import pytest
from config.settings import create_app
from instance.database import db
from flask_jwt_extended import create_access_token
from models.user import Users
from models.product import Products
from models.product_category import ProductCategories
from models.category import Categories


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
            username="vendoruser",
            first_name="Test",
            last_name="Vendor",
            email="vendor@mail.com",
            phone="081234567890",
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
        customer = Users(
            username="customeruser",
            first_name="Test",
            last_name="Customer",
            email="customer@mail.com",
            phone="089876543210",
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
        admin = Users(
            username="adminuser",
            first_name="Admin",
            last_name="User",
            email="admin@mail.com",
            phone="087654321098",
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
            name="Test Category",
            slug="test-category",
            vendor_id=vendor.id,
        )
        db.session.add(category)
        db.session.commit()

        app.test_category_id = category.id

        yield
        db.drop_all()


@pytest.fixture
def client(app, init_db):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def vendor_token(app):
    with app.app_context():
        return create_access_token(
            identity=str(1), additional_claims={"role": "vendor"}
        )


@pytest.fixture
def customer_token(app):
    with app.app_context():
        return create_access_token(
            identity=str(2), additional_claims={"role": "customer"}
        )


@pytest.fixture
def admin_token(app):
    with app.app_context():
        return create_access_token(identity=str(3), additional_claims={"role": "admin"})


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
            #location="Test City",
            featured=False,
            flash_sale=False,
            vendor_id=1,
        )
        db.session.add(product)

        # Assign the category (created in init_db)
        pc = ProductCategories(product_id=1, category_id=1)
        db.session.add(pc)

        db.session.commit()
        yield product
