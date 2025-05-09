import pytest
from datetime import datetime, timedelta
from instance.database import db
from models.voucher import Vouchers
from models.product import Products
from models.cart import Cart
from models.cart_item import CartItems


@pytest.fixture
def test_product(app):
    with app.app_context():
        product = Products(
            name="Test Product",
            slug="test-product",
            description="Product for voucher testing",
            price=100000,
            currency="IDR",
            stock_quantity=10,
            vendor_id=app.test_vendor_id,
            is_approved=True,
            discount_percentage=0,
            unit_quantity="1kg",
        )
        db.session.add(product)
        db.session.commit()
        return product.id


@pytest.fixture
def test_voucher(app):
    with app.app_context():
        voucher = Vouchers(
            code="TEST10",
            discount_percent=10,
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=1),
            vendor_id=app.test_vendor_id,
        )
        db.session.add(voucher)
        db.session.commit()
        return voucher.id


def test_deactivate_voucher(client, vendor_token, test_voucher, app):
    res = client.patch(
        f"/vouchers/{test_voucher}/deactivate",
        headers={"Authorization": f"Bearer {vendor_token}"}
    )
    print("Deactivate Voucher Response:", res.status_code, res.get_json())
    assert res.status_code == 200


def test_order_preview_with_voucher(client, customer_token, test_product, test_voucher, app):
    with app.app_context():
        product = db.session.get(Products, test_product)
        voucher = db.session.get(Vouchers, test_voucher)

        res = client.post(
            "/orders/preview",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "items": [{
                    "product_id": product.id,
                    "quantity": 1,
                    "unit_price": int(product.price)

                }],
                "voucher_code": voucher.code
            }
        )
        print("Order Preview Response:", res.status_code, res.get_json())
        assert res.status_code == 200
        assert b"total_after_discount" in res.data


def test_cart_summary_with_voucher(client, customer_token, test_product, test_voucher, app):
    with app.app_context():
        product = db.session.get(Products, test_product)
        voucher = db.session.get(Vouchers, test_voucher)

        cart = Cart.query.filter_by(user_id=app.test_customer_id).first()
        if not cart:
            cart = Cart(user_id=app.test_customer_id)
            db.session.add(cart)
            db.session.commit()

        cart_item = CartItems(cart_id=cart.id, product_id=product.id, quantity=2)
        db.session.add(cart_item)
        db.session.commit()

        res = client.get(
            f"/cart/summary?voucher_code={voucher.code}",
            headers={"Authorization": f"Bearer {customer_token}"}
        )
        print("Cart Summary Response:", res.status_code, res.get_json())
        assert res.status_code == 200
        assert b"discount_amount" in res.data
