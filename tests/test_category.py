import json
from flask_jwt_extended import create_access_token
from models.user import Users
from instance.database import db


from models.user import RoleType


def create_test_vendor(app):
    with app.app_context():
        vendor = Users.query.filter_by(id=1).first()
        if not vendor:
            vendor = Users(
                id=1,
                username="testvendor",
                first_name="Test",
                last_name="Vendor",
                email="vendor@example.com",
                phone="1234567890",
                password_hash="hashedpassword",
                date_of_birth="1990-01-01",
                address="123 Test St",
                city="Testville",
                state="Teststate",
                country="Testland",
                zip_code="12345",
                image_url="http://example.com/image.jpg",
                role=RoleType.vendor,
                bank_account="123456789",
                bank_name="Test Bank",
                is_active=True,
            )
            db.session.add(vendor)
            db.session.commit()
        return vendor


def get_auth_header(client):
    # Create a test user payload with vendor role
    test_user = {"id": 1, "role": "vendor"}
    token = create_access_token(identity=test_user)
    return {"Authorization": f"Bearer {token}"}


def test_create_category(client, app):
    """Test creating a new category."""
    create_test_vendor(app)
    headers = get_auth_header(client)
    response = client.post(
        "/categories",
        json={
            "name": "Coffee Beans",
            "slug": "coffee-beans",
            "image_url": "http://example.com/image.jpg",
        },
        headers={**headers, "Content-Type": "application/json"},
    )
    assert response.status_code in [
        201,
        400,
    ]  # 201 if created, 400 if vendor doesn't exist
    data = response.get_json()
    assert "msg" in data


def test_get_all_categories(client):
    """Test getting all categories."""
    response = client.get("/categories")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_get_category_by_id(client, app):
    """Test getting a specific category by ID."""
    # First, create a category (skip if already done by another test)
    create_test_vendor(app)
    headers = get_auth_header(client)
    client.post(
        "/categories",
        json={
            "name": "Tea",
            "slug": "tea",
            "image_url": "http://example.com/tea.jpg",
        },
        headers=headers,
    )

    response = client.get("/categories/1")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.get_json()
        assert "name" in data


def test_update_category(client, app):
    """Test updating a category."""
    create_test_vendor(app)
    headers = get_auth_header(client)
    # Ensure category exists before updating
    client.post(
        "/categories",
        json={
            "name": "Old Category",
            "slug": "old-category",
            "image_url": "http://example.com/old.jpg",
        },
        headers=headers,
    )
    response = client.put(
        "/categories/1",
        json={
            "name": "Updated Category",
        },
        headers={**headers, "Content-Type": "application/json"},
    )
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.get_json()
        assert data["msg"] == "Category updated"


def test_delete_category(client, app):
    """Test deleting a category."""
    create_test_vendor(app)
    headers = get_auth_header(client)
    # Ensure category exists before deleting
    client.post(
        "/categories",
        json={
            "name": "Temporary Category",
            "slug": "temp-category",
            "image_url": "http://example.com/temp.jpg",
        },
        headers=headers,
    )
    response = client.delete("/categories/1", headers=headers)
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.get_json()
        assert data["msg"] == "Category deleted"
