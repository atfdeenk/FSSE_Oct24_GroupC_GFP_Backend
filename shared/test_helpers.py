from models.user import Users
from models.product import Product
from instance.database import db


from werkzeug.security import generate_password_hash


def create_test_user(app):
    """Create and return a test user."""
    with app.app_context():
        hashed_password = generate_password_hash("hashedpassword")
        user = Users(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="testuser@example.com",
            phone="1234567890",
            password_hash=hashed_password,
            date_of_birth="1990-01-01",
            address="123 Test St",
            city="Testville",
            state="Teststate",
            country="Testland",
            zip_code="12345",
            image_url="http://example.com/image.jpg",
            role="customer",
            bank_account="123456789",
            bank_name="Test Bank",
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()

        # Refresh to make sure it's fully loaded
        db.session.refresh(user)

        # ✅ return only what you need (e.g. ID and email) to avoid DetachedInstanceError
        return {"id": user.id, "email": user.email}


def create_test_product(app):
    """Create and return a test product."""
    with app.app_context():
        product = Product(
            name="Test Product",
            slug="test-product",
            description="Test Description",
            price=10.0,
            stock_quantity=100,
            unit_quantity="pcs",
            image_url="http://example.com/product.jpg",
            location="Test Location",
            vendor_id=1,
        )
        db.session.add(product)
        db.session.commit()
        db.session.refresh(product)

        return {"id": product.id}
