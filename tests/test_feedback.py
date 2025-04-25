import pytest
from shared.auth_helpers import get_auth_header
from shared.test_helpers import create_test_user, create_test_product


# Helper to create feedback
def create_feedback(client, headers, product_id, rating=5, comment="Great product!"):
    return client.post(
        "/feedback",
        json={
            "product_id": product_id,
            "rating": rating,
            "comment": comment,
        },
        headers={**headers, "Content-Type": "application/json"},
    )


def test_create_feedback(client, app):
    with app.app_context():
        user = create_test_user(app)
        product = create_test_product(app)
        user_email = user["email"]
        product_id = product["id"]
    headers = get_auth_header(user_email)
    # product_id extracted inside app context

    response = create_feedback(client, headers, product_id)
    assert response.status_code == 201
    data = response.get_json()
    assert data["msg"] == "Feedback submitted"
    assert "id" in data


def test_get_feedback_by_product(client, app):
    with app.app_context():
        user = create_test_user(app)
        product = create_test_product(app)
        user_email = user["email"]
        product_id = product["id"]
    headers = get_auth_header(user_email)
    create_feedback(client, headers, product_id)
    # product_id extracted inside app context

    response = client.get(f"/feedback/product/{product_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1
    assert data[0]["product_id"] == product_id


def test_get_feedback_by_user(client, app):
    with app.app_context():
        user = create_test_user(app)
        product = create_test_product(app)
        user_email = user["email"]
        product_id = product["id"]
        user_id = user["id"]
    headers = get_auth_header(user_email)
    create_feedback(client, headers, product_id)
    # product_id extracted inside app context

    response = client.get(f"/feedback/user/{user_id}", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1
    assert data[0]["rating"] == 5


def test_get_all_feedback(client, app):
    with app.app_context():
        user = create_test_user(app)
        product = create_test_product(app)
        user_email = user["email"]
        product_id = product["id"]
    headers = get_auth_header(user_email)
    create_feedback(client, headers, product_id)
    # product_id extracted inside app context

    response = client.get("/feedback")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_delete_feedback(client, app):
    with app.app_context():
        user = create_test_user(app)
        product = create_test_product(app)
        user_email = user["email"]
        product_id = product["id"]
    headers = get_auth_header(user_email)
    create_resp = create_feedback(client, headers, product_id)
    feedback_id = create_resp.get_json()["id"]
    # product_id extracted inside app context

    delete_resp = client.delete(f"/feedback/{feedback_id}", headers=headers)
    assert delete_resp.status_code == 200
    assert delete_resp.get_json()["msg"] == "Feedback deleted"
