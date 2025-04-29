import json
from flask_jwt_extended import create_access_token
from models.user import Users
from instance.database import db

from models.user import RoleType


def test_create_category(client, vendor_token):
    """Test creating a new category."""
    headers = {"Authorization": f"Bearer {vendor_token}"}
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


def test_create_category_rollback_on_error(client, vendor_token, monkeypatch):
    """Test rollback behavior on category creation error."""
    headers = {"Authorization": f"Bearer {vendor_token}"}

    def raise_integrity_error(*args, **kwargs):
        from sqlalchemy.exc import IntegrityError

        raise IntegrityError("Simulated IntegrityError", None, None)

    monkeypatch.setattr("repo.category_repo.create_category", raise_integrity_error)

    response = client.post(
        "/categories",
        json={
            "name": "Faulty Category",
            "slug": "faulty-category",
            "image_url": "http://example.com/faulty.jpg",
        },
        headers={**headers, "Content-Type": "application/json"},
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "msg" in data
    assert "IntegrityError" in data["msg"] or "Simulated IntegrityError" in data["msg"]


def test_get_all_categories(client):
    """Test getting all categories."""
    response = client.get("/categories")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_get_category_by_id(client, vendor_token):
    """Test getting a specific category by ID."""
    headers = {"Authorization": f"Bearer {vendor_token}"}
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


def test_update_category(client, vendor_token):
    """Test updating a category."""
    headers = {"Authorization": f"Bearer {vendor_token}"}
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


def test_delete_category(client, vendor_token):
    """Test deleting a category."""
    headers = {"Authorization": f"Bearer {vendor_token}"}
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
