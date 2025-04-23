import pytest
from instance.database import db
from models.product import Products
from models.product_category import ProductCategories

@pytest.fixture
def seed_product(app):
    with app.app_context():
        product = Products(
            id=1,
            name="Sample Product",
            slug="sample-product",
            description="A test product",
            currency="IDR",
            price=10000.00,
            stock_quantity=10,
            unit_quantity="1 pack",
            vendor_id=1
        )
        db.session.add(product)
        db.session.commit()
        return product

def test_add_category_to_product(client, app, seed_product):
    with app.app_context():
        response = client.post(
            "/products/1/categories",
            json={"category_id": 1}
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["product_id"] == 1
        assert data["category_id"] == 1

def test_get_categories_of_product(client, app, seed_product):
    with app.app_context():
        # Ensure there's a category already assigned
        db.session.add(ProductCategories(product_id=1, category_id=1))
        db.session.commit()

        response = client.get("/products/1/categories")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert any(item["category_id"] == 1 for item in data)

def test_remove_category_from_product(client, app, seed_product):
    with app.app_context():
        db.session.add(ProductCategories(product_id=1, category_id=1))
        db.session.commit()

        response = client.delete("/products/1/categories/1")
        assert response.status_code == 200
        assert response.get_json()["message"] == "Category removed"
