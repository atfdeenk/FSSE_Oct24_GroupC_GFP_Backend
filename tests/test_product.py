import pytest
from decimal import Decimal
from models.product import Products
from instance.database import db

def test_get_all_products(client):
    res = client.get("/products")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)

def test_create_product_authorized(client, vendor_token):
    headers = {
        "Authorization": f"Bearer {vendor_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": "Test Product",
        "slug": "test-product",
        "description": "A product created in test",
        "currency": "IDR",
        "price": "15000.00",  # Changed back to string format
        "discount_percentage": 0,
        "stock_quantity": 10,
        "unit_quantity": "pcs",
        "location": "Jakarta",
        "image_url": "http://example.com/image.jpg",
        "featured": False,
        "flash_sale": False,
        "vendor_id": 1,
        "category_id": 1  # Added category_id
    }
    res = client.post("/products", json=payload, headers=headers)
    assert res.status_code == 201

def test_create_product_unauthorized_role(client, user_token):
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": "Unauthorized Product",
        "slug": "unauth-product",
        "description": "Should not be allowed",
        "currency": "IDR",
        "price": "10000.00",  # Changed back to string format
        "discount_percentage": 0,
        "stock_quantity": 5,
        "unit_quantity": "pcs",
        "location": "Bandung",
        "image_url": "http://example.com/image2.jpg",
        "featured": False,
        "flash_sale": False,
        "vendor_id": 1,
        "category_id": 1  # Added category_id
    }
    res = client.post("/products", json=payload, headers=headers)
    assert res.status_code == 403

def test_delete_product_as_admin(client, admin_token):
    with client.application.app_context():
        product = Products(
            name="Delete Me",
            slug="delete-me",
            description="To be deleted",
            currency="IDR",
            price=Decimal("10000.00"),
            discount_percentage=0,
            stock_quantity=1,
            unit_quantity="pcs",
            vendor_id=1,
            category_id=1,  # Added category_id
            location="Test City",
            image_url="http://example.com/image.jpg",
            featured=False,
            flash_sale=False
        )
        db.session.add(product)
        db.session.commit()
        product_id = product.id

    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.delete(f"/products/{product_id}", headers=headers)
    assert res.status_code == 200
