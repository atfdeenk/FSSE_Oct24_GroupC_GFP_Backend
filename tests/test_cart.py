import pytest
from instance.database import db
from models.product import Products
from models.cart_item import CartItems


@pytest.fixture
def seed_product(app):
    with app.app_context():
        product = Products(
            id=1,
            name="Test Product",
            slug="test-product",
            description="Product for cart testing",
            currency="IDR",
            price=15000.00,
            stock_quantity=20,
            unit_quantity="1 pc",
            vendor_id=1,
        )
        db.session.add(product)

        # ✅ Add a customer user with id=2
        from models.user import Users

        customer = Users(
            username="testcustomer",
            first_name="Cart",
            last_name="User",
            email="cartuser@mail.com",
            phone="081234567892",
            password_hash="test",
            date_of_birth="1991-01-01",
            address="Cart St",
            city="Jakarta",
            state="DKI Jakarta",
            country="Indonesia",
            zip_code="67890",
            image_url="https://example.com/customer.png",
            role="customer",
            bank_account="1112223334",
            bank_name="Mandiri",
            is_active=True,
        )
        db.session.add(customer)

        db.session.commit()
        yield
        db.session.query(Products).delete()
        db.session.query(Users).filter(Users.id == 2).delete()
        db.session.commit()


def test_create_and_get_cart(client, customer_token):
    response = client.get(
        "/cart", headers={"Authorization": f"Bearer {customer_token}"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "cart_id" in data and "user_id" in data


def test_add_item_to_cart(client, customer_token, seed_product):
    response = client.post(
        "/cart/items",
        json={"product_id": 1, "quantity": 2},
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["product_id"] == 1
    assert data["quantity"] == 2


def test_get_cart_items(client, customer_token, seed_product):
    client.post(
        "/cart/items",
        json={"product_id": 1, "quantity": 3},
        headers={"Authorization": f"Bearer {customer_token}"},
    )

    response = client.get(
        "/cart/items", headers={"Authorization": f"Bearer {customer_token}"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert data[0]["product_id"] == 1


def test_update_cart_item_quantity(client, app, customer_token, seed_product):
    with app.app_context():
        from models.cart import Cart

        cart = Cart(user_id=2)
        db.session.add(cart)
        db.session.commit()

        item = CartItems(cart_id=cart.id, product_id=1, quantity=2)
        db.session.add(item)
        db.session.commit()

        response = client.patch(
            f"/cart/items/{item.id}",
            json={"quantity": 5},
            headers={"Authorization": f"Bearer {customer_token}"},
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["quantity"] == 5


def test_remove_cart_item(client, app, customer_token, seed_product):
    with app.app_context():
        from models.cart import Cart

        cart = Cart(user_id=2)
        db.session.add(cart)
        db.session.commit()

        item = CartItems(cart_id=cart.id, product_id=1, quantity=1)
        db.session.add(item)
        db.session.commit()

        response = client.delete(
            f"/cart/items/{item.id}",
            headers={"Authorization": f"Bearer {customer_token}"},
        )
        assert response.status_code == 200
        assert response.get_json()["message"] == "Item removed"
