import pytest
from decimal import Decimal
from models.product import Products
from models.product_category import ProductCategories
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
        "price": "15000.00",
        "discount_percentage": 0,
        "stock_quantity": 10,
        "unit_quantity": "pcs",
        "location": "Jakarta",
        "image_url": "http://example.com/image.jpg",
        "featured": False,
        "flash_sale": False
        # "vendor_id": 1,  # Remove if not required by API
        # "category_ids": [1]  # Remove if not required by API
    }
    res = client.post("/products", json=payload, headers=headers)
    if res.status_code != 201:
        print("Response JSON:", res.get_json())
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
        "price": "10000.00",
        "discount_percentage": 0,
        "stock_quantity": 5,
        "unit_quantity": "pcs",
        "location": "Bandung",
        "image_url": "http://example.com/image2.jpg",
        "featured": False,
        "flash_sale": False
        # "vendor_id": 1,
        # "category_ids": [1]
    }
    res = client.post("/products", json=payload, headers=headers)
    if res.status_code != 403:
        print("Response JSON:", res.get_json())
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
        location="Test City",
        image_url="http://example.com/image.jpg",
        featured=False,
        flash_sale=False
    )
    db.session.add(product)
    db.session.flush()  # ensures product.id is assigned

    # Many-to-many association
    db.session.add(ProductCategories(product_id=product.id, category_id=1))

    db.session.commit()
    product_id = product.id