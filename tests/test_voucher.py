import pytest
from datetime import datetime, timedelta
from flask_jwt_extended import decode_token

@pytest.fixture
def test_voucher(app):
    from models.voucher import Vouchers
    from instance.database import db

    with app.app_context():
        voucher = Vouchers(
            code="SAVE20",
            discount_percent=20,
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=1)
        )
        db.session.add(voucher)
        db.session.commit()
        return voucher.id  # Return only ID to avoid DetachedInstanceError

def test_get_all_vouchers(client):
    response = client.get("/vouchers")
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_create_voucher_admin(client, admin_token):
    res = client.post(
        "/vouchers",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "code": "POSTMAN30",
            "discount_percent": 30,
            "is_active": True,
            "expires_at": "2025-06-30T00:00:00"
        }
    )
    assert res.status_code == 201
    assert "id" in res.json

def test_deactivate_voucher(client, admin_token, test_voucher):
    res = client.patch(
        f"/vouchers/{test_voucher}/deactivate",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    assert "deactivated" in res.json["msg"].lower()

def test_order_preview_with_voucher(client, admin_token, test_voucher):
    res = client.post(
        "/orders/preview",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "items": [{"product_id": 1, "quantity": 2, "unit_price": 10000}],
            "voucher_code": "SAVE20"
        }
    )
    assert res.status_code == 200
    assert res.json["total_before_discount"] == 20000
    assert res.json["discount_amount"] == 4000.0
    assert res.json["total_after_discount"] == 16000.0

def test_cart_summary_with_voucher(client, customer_token, test_voucher, app):
    from models.cart_item import CartItems
    from models.product import Products
    from models.cart import Cart
    from instance.database import db

    user_id = decode_token(customer_token)["sub"]

    with app.app_context():
        product = Products(
            id=99,
            name="Test Coffee",
            slug="test-coffee",
            description="Test description",
            price=10000,
            currency="IDR",
            stock_quantity=10,
            vendor_id=1,
            is_approved=True,
            discount_percentage=0,
            unit_quantity="250g",
        )
        db.session.add(product)
        db.session.commit()

        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.session.add(cart)
            db.session.commit()

        cart_item = CartItems(cart_id=cart.id, product_id=product.id, quantity=2)
        db.session.add(cart_item)
        db.session.commit()

    res = client.get(
        f"/cart/summary?voucher_code=SAVE20",
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    assert res.status_code == 200
    assert res.json["total_before_discount"] == 20000
    assert res.json["discount_amount"] == 4000.0
    assert res.json["total_after_discount"] == 16000.0