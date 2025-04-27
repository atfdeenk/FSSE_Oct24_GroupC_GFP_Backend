import json
import pytest
from unittest.mock import patch


def patch_jwt_identity(user_id):
    return patch("route.order_route.get_jwt_identity", return_value={"id": user_id})


@patch_jwt_identity(2)
def test_create_order_success(
    mock_get_jwt_identity, client, customer_token, seed_product
):
    headers = {"Authorization": f"Bearer {customer_token}"}
    data = {
        "vendor_id": seed_product.vendor_id,
        "items": [{"product_id": seed_product.id, "quantity": 2, "unit_price": 85000}],
    }
    response = client.post(
        "/orders",
        data=json.dumps(data),
        headers=headers,
        content_type="application/json",
    )
    assert response.status_code == 201
    json_data = response.get_json()
    assert "order_id" in json_data
    assert json_data["msg"] == "Order created"


def patch_jwt_identity(user_id):
    return patch("route.order_route.get_jwt_identity", return_value={"id": user_id})


@patch_jwt_identity(2)
def test_get_order_success(mock_get_jwt_identity, client, customer_token, seed_product):
    # First create an order
    headers = {"Authorization": f"Bearer {customer_token}"}
    data = {
        "vendor_id": seed_product.vendor_id,
        "items": [
            {
                "product_id": seed_product.id,
                "quantity": 1,
                "unit_price": float(seed_product.price),
            }
        ],
    }
    create_resp = client.post(
        "/orders",
        data=json.dumps(data),
        headers=headers,
        content_type="application/json",
    )
    order_id = create_resp.get_json()["order_id"]

    # Get the order
    response = client.get(f"/orders/{order_id}", headers=headers)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "order" in json_data
    assert json_data["order"]["id"] == order_id
    # Check order items keys
    items = json_data["order"]["items"]
    assert isinstance(items, list)
    assert "product_id" in items[0]
    assert "quantity" in items[0]
    assert "unit_price" in items[0]


def patch_jwt_identity(user_id):
    return patch("route.order_route.get_jwt_identity", return_value={"id": user_id})


@patch_jwt_identity(2)
def test_get_user_orders_success(mock_get_jwt_identity, client, customer_token):
    headers = {"Authorization": f"Bearer {customer_token}"}
    response = client.get("/orders", headers=headers)
    assert response.status_code == 200
    json_data = response.get_json()
    assert isinstance(json_data, list)


def test_get_user_orders_unauthorized(client):
    response = client.get("/orders")
    assert response.status_code == 401


def patch_jwt_identity(user_id):
    return patch("route.order_route.get_jwt_identity", return_value={"id": user_id})


@patch_jwt_identity(2)
def test_update_order_status_success(
    mock_get_jwt_identity, client, customer_token, seed_product
):
    headers = {"Authorization": f"Bearer {customer_token}"}
    # Create order first
    data = {
        "vendor_id": seed_product.vendor_id,
        "items": [{"product_id": seed_product.id, "quantity": 1, "unit_price": 85000}],
    }
    create_resp = client.post(
        "/orders",
        data=json.dumps(data),
        headers=headers,
        content_type="application/json",
    )
    order_id = create_resp.get_json()["order_id"]

    # Update status
    update_data = {"status": "shipped"}
    response = client.put(
        f"/orders/{order_id}/status",
        data=json.dumps(update_data),
        headers=headers,
        content_type="application/json",
    )
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["msg"] == "Order status updated"


def test_update_order_status_missing_status(client, customer_token):
    headers = {"Authorization": f"Bearer {customer_token}"}
    response = client.put(
        "/orders/1/status",
        data=json.dumps({}),
        headers=headers,
        content_type="application/json",
    )
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["msg"] == "Status is required"


def test_update_order_status_not_found(client, customer_token):
    headers = {"Authorization": f"Bearer {customer_token}"}
    update_data = {"status": "shipped"}
    response = client.put(
        "/orders/999999/status",
        data=json.dumps(update_data),
        headers=headers,
        content_type="application/json",
    )
    assert response.status_code == 404


def test_update_order_status_unauthorized(client):
    update_data = {"status": "shipped"}
    response = client.put(
        "/orders/1/status",
        data=json.dumps(update_data),
        content_type="application/json",
    )
    assert response.status_code == 401


def patch_jwt_identity(user_id):
    return patch("route.order_route.get_jwt_identity", return_value={"id": user_id})


@patch_jwt_identity(2)
def test_delete_order_success(
    mock_get_jwt_identity, client, customer_token, seed_product
):
    headers = {"Authorization": f"Bearer {customer_token}"}
    # Create order first
    data = {
        "vendor_id": seed_product.vendor_id,
        "items": [{"product_id": seed_product.id, "quantity": 1, "unit_price": 85000}],
    }
    create_resp = client.post(
        "/orders",
        data=json.dumps(data),
        headers=headers,
        content_type="application/json",
    )
    order_id = create_resp.get_json()["order_id"]

    # Delete order
    response = client.delete(f"/orders/{order_id}", headers=headers)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["msg"] == "Order deleted"


def patch_jwt_identity(user_id):
    return patch("route.order_route.get_jwt_identity", return_value={"id": user_id})


@patch_jwt_identity(2)
def test_get_order_success(mock_get_jwt_identity, client, customer_token, seed_product):
    # First create an order
    headers = {"Authorization": f"Bearer {customer_token}"}
    data = {
        "vendor_id": seed_product.vendor_id,
        "items": [
            {
                "product_id": seed_product.id,
                "quantity": 1,
                "unit_price": float(seed_product.price),
            }
        ],
    }
    create_resp = client.post(
        "/orders",
        data=json.dumps(data),
        headers=headers,
        content_type="application/json",
    )
    order_id = create_resp.get_json()["order_id"]

    # Get the order
    response = client.get(f"/orders/{order_id}", headers=headers)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "order" in json_data
    assert json_data["order"]["id"] == order_id
    # Check order items keys
    items = json_data["order"]["items"]
    assert isinstance(items, list)
    assert "product_id" in items[0]
    assert "quantity" in items[0]
    assert "unit_price" in items[0]


def test_create_order_no_items(client, customer_token):
    headers = {"Authorization": f"Bearer {customer_token}"}
    data = {"items": []}
    response = client.post(
        "/orders",
        data=json.dumps(data),
        headers=headers,
        content_type="application/json",
    )
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["msg"] == "No items to order"


def test_create_order_unauthorized(client):
    data = {"items": [{"product_id": 1, "quantity": 1}]}
    response = client.post(
        "/orders", data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 401


from unittest.mock import patch


def patch_jwt_identity(user_id):
    return patch("route.order_route.get_jwt_identity", return_value={"id": user_id})


@patch_jwt_identity(2)
def test_get_order_success(mock_get_jwt_identity, client, customer_token, seed_product):
    # First create an order
    headers = {"Authorization": f"Bearer {customer_token}"}
    data = {
        "vendor_id": seed_product.vendor_id,
        "items": [
            {
                "product_id": seed_product.id,
                "quantity": 1,
                "unit_price": float(seed_product.price),
            }
        ],
    }
    create_resp = client.post(
        "/orders",
        data=json.dumps(data),
        headers=headers,
        content_type="application/json",
    )
    order_id = create_resp.get_json()["order_id"]

    # Get the order
    response = client.get(f"/orders/{order_id}", headers=headers)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "order" in json_data
    assert json_data["order"]["id"] == order_id
    # Check order items keys
    items = json_data["order"]["items"]
    assert isinstance(items, list)
    assert "product_id" in items[0]
    assert "quantity" in items[0]
    assert "unit_price" in items[0]


def test_get_order_not_found(client, customer_token):
    headers = {"Authorization": f"Bearer {customer_token}"}
    response = client.get("/orders/999999", headers=headers)
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data["msg"] == "Order not found"


def test_get_order_unauthorized(client):
    response = client.get("/orders/1")
    assert response.status_code == 401


from unittest.mock import patch


def patch_jwt_identity(user_id):
    return patch("route.order_route.get_jwt_identity", return_value={"id": user_id})


@patch_jwt_identity(2)
def test_get_user_orders_success(mock_get_jwt_identity, client, customer_token):
    headers = {"Authorization": f"Bearer {customer_token}"}
    response = client.get("/orders", headers=headers)
    assert response.status_code == 200
    json_data = response.get_json()
    assert isinstance(json_data, list)


def test_get_user_orders_unauthorized(client):
    response = client.get("/orders")
    assert response.status_code == 401


from unittest.mock import patch


def patch_jwt_identity(user_id):
    return patch("route.order_route.get_jwt_identity", return_value={"id": user_id})


@patch_jwt_identity(2)
def test_update_order_status_success(
    mock_get_jwt_identity, client, customer_token, seed_product
):
    headers = {"Authorization": f"Bearer {customer_token}"}
    # Create order first
    data = {
        "vendor_id": seed_product.vendor_id,
        "items": [{"product_id": seed_product.id, "quantity": 1, "unit_price": 85000}],
    }
    create_resp = client.post(
        "/orders",
        data=json.dumps(data),
        headers=headers,
        content_type="application/json",
    )
    order_id = create_resp.get_json()["order_id"]

    # Update status
    update_data = {"status": "shipped"}
    response = client.put(
        f"/orders/{order_id}/status",
        data=json.dumps(update_data),
        headers=headers,
        content_type="application/json",
    )
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["msg"] == "Order status updated"


def test_update_order_status_missing_status(client, customer_token):
    headers = {"Authorization": f"Bearer {customer_token}"}
    response = client.put(
        "/orders/1/status",
        data=json.dumps({}),
        headers=headers,
        content_type="application/json",
    )
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["msg"] == "Status is required"


def test_update_order_status_not_found(client, customer_token):
    headers = {"Authorization": f"Bearer {customer_token}"}
    update_data = {"status": "shipped"}
    response = client.put(
        "/orders/999999/status",
        data=json.dumps(update_data),
        headers=headers,
        content_type="application/json",
    )
    assert response.status_code == 404


def test_update_order_status_unauthorized(client):
    update_data = {"status": "shipped"}
    response = client.put(
        "/orders/1/status",
        data=json.dumps(update_data),
        content_type="application/json",
    )
    assert response.status_code == 401


from unittest.mock import patch


def patch_jwt_identity(user_id):
    return patch("route.order_route.get_jwt_identity", return_value={"id": user_id})


@patch_jwt_identity(2)
def test_delete_order_success(
    mock_get_jwt_identity, client, customer_token, seed_product
):
    headers = {"Authorization": f"Bearer {customer_token}"}
    # Create order first
    data = {
        "vendor_id": seed_product.vendor_id,
        "items": [{"product_id": seed_product.id, "quantity": 1, "unit_price": 85000}],
    }
    create_resp = client.post(
        "/orders",
        data=json.dumps(data),
        headers=headers,
        content_type="application/json",
    )
    order_id = create_resp.get_json()["order_id"]

    # Delete order
    response = client.delete(f"/orders/{order_id}", headers=headers)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["msg"] == "Order deleted"


def test_delete_order_not_found(client, customer_token):
    headers = {"Authorization": f"Bearer {customer_token}"}
    response = client.delete("/orders/999999", headers=headers)
    assert response.status_code == 404


def test_delete_order_unauthorized(client):
    response = client.delete("/orders/1")
    assert response.status_code == 401
