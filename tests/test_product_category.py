import pytest
from instance.database import db
from models.product import Products
from models.product_category import ProductCategories


@pytest.fixture
def seed_product(app):
    with app.app_context():
        product = Products(
            id=1,
            name="Category Test Product",
            slug="category-test-product",
            description="Used for category tests",
            currency="IDR",
            price=50000.00,
            stock_quantity=10,
            unit_quantity="250g",
            vendor_id=1,
        )
        db.session.add(product)
        db.session.commit()
        yield
        db.session.query(Products).delete()
        db.session.commit()


def test_add_category_to_product(client, app, seed_product, vendor_token):
    with app.app_context():
        response = client.post(
            "/products/1/categories",
            headers={"Authorization": f"Bearer {vendor_token}"},
            json={"category_id": 1},
        )
        assert response.status_code == 201
        assert "product_id" in response.json
        assert "category_id" in response.json


def test_get_categories_of_product(client, app, seed_product, vendor_token):
    with app.app_context():
        db.session.add(ProductCategories(product_id=1, category_id=1))
        db.session.commit()

        response = client.get(
            "/products/1/categories",
            headers={"Authorization": f"Bearer {vendor_token}"},
        )
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert any(rel["category_id"] == 1 for rel in response.json)


def test_remove_category_from_product(client, app, seed_product, vendor_token):
    with app.app_context():
        db.session.add(ProductCategories(product_id=1, category_id=1))
        db.session.commit()

        response = client.delete(
            "/products/1/categories/1",
            headers={"Authorization": f"Bearer {vendor_token}"},
        )
        assert response.status_code == 200
        assert response.json["message"] == "Category removed"
