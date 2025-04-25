import pytest
from instance.database import db
from models.product import Products
from models.product_image import ProductImages

@pytest.fixture
def seed_product(app):
    with app.app_context():
        product = Products(
            id=1,
            name="Image Test Product",
            slug="image-test-product",
            description="Product for image testing",
            currency="IDR",
            price=20000.00,
            stock_quantity=5,
            unit_quantity="1 bottle",
            vendor_id=1
        )
        db.session.add(product)
        db.session.commit()
        yield
        db.session.query(Products).delete()
        db.session.commit()

def test_create_product_images(client, app, seed_product, vendor_token):
    with app.app_context():
        response = client.post(
            "/products/1/images",
            json={
                "image1_url": "https://example.com/image1.jpg",
                "image2_url": "https://example.com/image2.jpg",
                "image3_url": "https://example.com/image3.jpg"
            },
            headers={"Authorization": f"Bearer {vendor_token}"}
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["product_id"] == 1
        assert "image1_url" in data

def test_create_image_unauthorized(client, app, seed_product):
    with app.app_context():
        response = client.post(
            "/products/1/images",
            json={"image1_url": "unauthorized.jpg"}
        )
        assert response.status_code in [401, 403]

def test_get_product_images(client, app, seed_product):
    with app.app_context():
        db.session.add(ProductImages(
            product_id=1,
            image1_url="https://example.com/image1.jpg",
            image2_url="https://example.com/image2.jpg",
            image3_url="https://example.com/image3.jpg"
        ))
        db.session.commit()

        response = client.get("/products/1/images")
        assert response.status_code == 200
        data = response.get_json()
        assert data["product_id"] == 1
        assert data["image1_url"] == "https://example.com/image1.jpg"

def test_update_product_images(client, app, seed_product, vendor_token):
    with app.app_context():
        db.session.add(ProductImages(
            product_id=1,
            image1_url="https://example.com/image1.jpg",
            image2_url="https://example.com/image2.jpg",
            image3_url="https://example.com/image3.jpg"
        ))
        db.session.commit()

        response = client.put(
            "/products/1/images",
            json={"image2_url": "https://updated.com/image2.jpg"},
            headers={"Authorization": f"Bearer {vendor_token}"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["image2_url"] == "https://updated.com/image2.jpg"

def test_delete_product_images(client, app, seed_product, vendor_token):
    with app.app_context():
        db.session.add(ProductImages(
            product_id=1,
            image1_url="https://example.com/image1.jpg"
        ))
        db.session.commit()

        response = client.delete(
            "/products/1/images",
            headers={"Authorization": f"Bearer {vendor_token}"}
        )
        assert response.status_code == 200
        assert response.get_json()["message"] == "Images deleted"
