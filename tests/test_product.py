import pytest
from decimal import Decimal
from models.product import Products
from models.product_category import ProductCategories
from instance.database import db


def test_get_all_products(client, seed_product):
    res = client.get("/products")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data["products"], list)  # Access "products" key
    assert "total" in data
    assert data["total"] >= 1


def test_create_product_authorized(client, vendor_token):
    headers = {
        "Authorization": f"Bearer {vendor_token}",
        "Content-Type": "application/json",
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
        # "location": "Jakarta",
        "image_url": "http://example.com/image.jpg",
        "featured": False,
        "flash_sale": False,
        # "vendor_id": 1,  # Remove if not required by API
        # "category_ids": [1]  # Remove if not required by API
    }
    res = client.post("/products", json=payload, headers=headers)
    if res.status_code != 201:
        print("Response JSON:", res.get_json())
    assert res.status_code == 201


def test_create_product_unauthorized_role(client, customer_token):
    headers = {
        "Authorization": f"Bearer {customer_token}",
        "Content-Type": "application/json",
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
        # "location": "Bandung",
        "image_url": "http://example.com/image2.jpg",
        "featured": False,
        "flash_sale": False,
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
            # location="Test City",
            image_url="http://example.com/image.jpg",
            featured=False,
            flash_sale=False,
        )
        db.session.add(product)
        db.session.flush()  # ensures product.id is assigned

        # Many-to-many association
        db.session.add(ProductCategories(product_id=product.id, category_id=1))

        db.session.commit()
        product_id = product.id


def test_update_product(client, vendor_token):
    headers = {
        "Authorization": f"Bearer {vendor_token}",
        "Content-Type": "application/json",
    }

    # Create product first
    payload = {
        "name": "To Update",
        "slug": "to-update",
        "description": "Old Desc",
        "currency": "IDR",
        "price": "20000.00",
        "discount_percentage": 0,
        "stock_quantity": 15,
        "unit_quantity": "pcs",
        # "location": "Medan",
        "image_url": "http://example.com/update.jpg",
        "featured": False,
        "flash_sale": False,
    }
    create_res = client.post("/products", json=payload, headers=headers)
    product_id = create_res.get_json()["id"]

    # Update
    update_payload = {"description": "Updated Desc", "price": "22000.00"}
    update_res = client.put(
        f"/products/{product_id}", json=update_payload, headers=headers
    )
    assert update_res.status_code == 200
    assert update_res.get_json()["description"] == "Updated Desc"
    assert float(update_res.get_json()["price"]) == 22000.00


def test_create_product_missing_fields(client, vendor_token):
    headers = {
        "Authorization": f"Bearer {vendor_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "name": "Incomplete Product"
        # Missing all required fields
    }
    res = client.post("/products", json=payload, headers=headers)
    assert res.status_code == 400 or res.status_code == 422

def test_get_single_product(client, app, vendor_token):
    headers = {
        "Authorization": f"Bearer {vendor_token}",
        "Content-Type": "application/json"
    }

    # Step 1: Create the product
    create_payload = {
        "name": "Single Product",
        "slug": "single-product",
        "description": "For single fetch",
        "currency": "IDR",
        "price": "25000.00",
        "stock_quantity": 5,
        "unit_quantity": "box",
        "image_url": "http://example.com/single.jpg"
    }

    create_res = client.post("/products", json=create_payload, headers=headers)
    assert create_res.status_code == 201

    product_id = create_res.get_json()["id"]

    # Step 2: Approve the product manually in the DB
    with app.app_context():
        product = db.session.get(Products, product_id)
        product.is_approved = True
        db.session.commit()

    # Step 3: Fetch the product by ID (public access)
    get_res = client.get(f"/products/{product_id}")
    assert get_res.status_code == 200
    data = get_res.get_json()
    assert data["id"] == product_id
    assert data["name"] == "Single Product"



def test_update_product_unauthorized(client, customer_token):
    headers = {"Authorization": f"Bearer {customer_token}"}
    update_payload = {"description": "Should be denied"}
    res = client.put("/products/1", json=update_payload, headers=headers)
    assert res.status_code in [401, 403]


def test_vendor_can_delete_own_product(client, vendor_token):
    headers = {
        "Authorization": f"Bearer {vendor_token}",
        "Content-Type": "application/json"
    }

    # Create a product under the vendor
    create_payload = {
        "name": "Vendor Deletable Product",
        "slug": "vendor-deletable",
        "description": "Owned by vendor",
        "currency": "IDR",
        "price": "15000.00",
        "stock_quantity": 5,
        "unit_quantity": "pcs",
        "image_url": "http://example.com/vendor-delete.jpg"
    }
    res = client.post("/products", json=create_payload, headers=headers)
    assert res.status_code == 201
    product_id = res.get_json()["id"]

    # Delete as the same vendor
    delete_res = client.delete(f"/products/{product_id}", headers=headers)
    assert delete_res.status_code == 200
    assert "message" in delete_res.get_json()


def test_admin_can_delete_product(client, admin_token, vendor_token):
    headers_vendor = {
        "Authorization": f"Bearer {vendor_token}",
        "Content-Type": "application/json"
    }

    # Vendor creates product
    create_payload = {
        "name": "Admin Deletable Product",
        "slug": "admin-deletable",
        "description": "Will be deleted by admin",
        "currency": "IDR",
        "price": "20000.00",
        "stock_quantity": 10,
        "unit_quantity": "pcs",
        "image_url": "http://example.com/admin-delete.jpg"
    }
    res = client.post("/products", json=create_payload, headers=headers_vendor)
    assert res.status_code == 201
    product_id = res.get_json()["id"]

    # Admin deletes it
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    delete_res = client.delete(f"/products/{product_id}", headers=headers_admin)
    assert delete_res.status_code == 200
    assert "message" in delete_res.get_json()



def test_get_product_invalid_id(client):
    res = client.get("/products/99999")
    assert res.status_code == 404


def test_update_nonexistent_product(client, vendor_token):
    headers = {
        "Authorization": f"Bearer {vendor_token}",
        "Content-Type": "application/json"
    }
    payload = {"name": "Should not update"}
    res = client.put("/products/999999", json=payload, headers=headers)
    assert res.status_code == 404

def test_delete_nonexistent_product(client, vendor_token):
    headers = {"Authorization": f"Bearer {vendor_token}"}
    res = client.delete("/products/999999", headers=headers)
    assert res.status_code == 404


def test_create_product_duplicate_slug(client, vendor_token):
    headers = {
        "Authorization": f"Bearer {vendor_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": "Duplicate Slug",
        "slug": "duplicate-slug",
        "description": "First one",
        "currency": "IDR",
        "price": "20000.00",
        "stock_quantity": 5,
        "unit_quantity": "pcs",
        "image_url": "http://example.com/dup.jpg"
    }
    client.post("/products", json=payload, headers=headers)
    res = client.post("/products", json=payload, headers=headers)
    assert res.status_code in [400, 409]

def test_create_product_invalid_price_format(client, vendor_token):
    headers = {
        "Authorization": f"Bearer {vendor_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": "Bad Price Product",
        "slug": "bad-price-product",
        "description": "Invalid price field",
        "currency": "IDR",
        "price": "not-a-number",  # ⚡ BAD price
        "stock_quantity": 5,
        "unit_quantity": "pcs",
        "image_url": "http://example.com/bad.jpg"
    }
    res = client.post("/products", json=payload, headers=headers)
    assert res.status_code == 400

def test_approve_product_as_admin(client, admin_token, vendor_token):
    headers = {"Authorization": f"Bearer {vendor_token}"}
    payload = {
        "name": "Need Approval",
        "slug": "need-approval",
        "description": "Waiting for admin approval",
        "currency": "IDR",
        "price": "12345.00",
        "stock_quantity": 3,
        "unit_quantity": "pcs",
        "image_url": "http://example.com/approve.jpg"
    }

    res = client.post("/products", json=payload, headers=headers)
    product_id = res.get_json()["id"]

    # Approve with admin
    headers_admin = {
    "Authorization": f"Bearer {admin_token}",
    "Content-Type": "application/json"
}

    approve_res = client.patch(f"/products/{product_id}/approve", headers=headers_admin)
    assert approve_res.status_code == 200
    assert approve_res.get_json()["is_approved"] is True

def test_reject_product_as_admin(client, admin_token, vendor_token):
    headers_vendor = {
        "Authorization": f"Bearer {vendor_token}",
        "Content-Type": "application/json"
    }

    # Step 1: Vendor creates product
    payload = {
        "name": "Reject Me",
        "slug": "reject-me",
        "description": "Should be rejected by admin",
        "currency": "IDR",
        "price": "18000.00",
        "stock_quantity": 4,
        "unit_quantity": "pcs",
        "image_url": "http://example.com/reject.jpg"
    }
    res = client.post("/products", json=payload, headers=headers_vendor)
    assert res.status_code == 201
    product_id = res.get_json()["id"]

    # Step 2: Admin rejects the product
    headers_admin = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }

    reject_res = client.patch(f"/products/{product_id}/reject", headers=headers_admin)
    assert reject_res.status_code == 200
    assert reject_res.get_json()["is_approved"] is False

def test_admin_can_fetch_only_unapproved_products(client, admin_token, vendor_token):
    headers_vendor = {
        "Authorization": f"Bearer {vendor_token}",
        "Content-Type": "application/json"
    }

    # Step 1: Vendor creates an unapproved product
    payload = {
        "name": "Unapproved Product",
        "slug": "unapproved-product",
        "description": "Pending admin approval",
        "currency": "IDR",
        "price": "10000.00",
        "stock_quantity": 5,
        "unit_quantity": "pcs",
        "image_url": "http://example.com/unapproved.jpg"
    }
    create_res = client.post("/products", json=payload, headers=headers_vendor)
    assert create_res.status_code == 201
    product_id = create_res.get_json()["id"]

    # Step 2: Admin fetches ONLY unapproved products
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    fetch_res = client.get("/products?only_unapproved=true", headers=headers_admin)
    assert fetch_res.status_code == 200
    data = fetch_res.get_json()

    # Step 3: Confirm that our product is in the list and not approved
    assert any(p["id"] == product_id and p["is_approved"] is False for p in data["products"])

