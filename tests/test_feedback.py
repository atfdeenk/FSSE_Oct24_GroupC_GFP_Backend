import pytest
from instance.database import db
import json
from unittest.mock import patch


def test_create_feedback(client, customer_token, seed_product):
    payload = {"product_id": seed_product.id, "rating": 4, "comment": "Great coffee!"}
    response = client.post(
        "/feedback",
        headers={"Authorization": f"Bearer {customer_token}"},
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "feedback" in data
    assert data["msg"] == "Feedback submitted successfully"


def test_create_feedback_rollback(client, customer_token, seed_product):
    payload = {"product_id": seed_product.id, "rating": 4, "comment": "Great coffee!"}
    with patch("repo.feedback_repo.create_feedback") as mock_create_feedback:
        mock_create_feedback.side_effect = Exception("DB error")
        response = client.post(
            "/feedback",
            headers={"Authorization": f"Bearer {customer_token}"},
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert data["msg"] == "Failed to create feedback"


def test_get_feedback_by_product(client, customer_token, seed_product):
    # First, create feedback
    client.post(
        "/feedback",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={
            "product_id": seed_product.id,
            "rating": 5,
            "comment": "Amazing product!",
        },
    )

    # Then retrieve it
    response = client.get(f"/feedback/product/{seed_product.id}")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, dict)
    assert "feedback" in data
    assert len(data["feedback"]) >= 1
    assert data["feedback"][0]["product_id"] == seed_product.id


def test_get_feedback_by_user(client, app, init_db, customer_token, seed_product):
    with app.app_context():
        from models.feedback import Feedbacks

        # Create feedback for customer (id=2)
        feedback = Feedbacks(
            user_id=2, product_id=seed_product.id, rating=5, comment="Excellent product"
        )
        db.session.add(feedback)
        db.session.commit()

        response = client.get(
            f"/feedback/user/2", headers={"Authorization": f"Bearer {customer_token}"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert "feedback" in data
        assert any(fb["comment"] == "Excellent product" for fb in data["feedback"])


def test_get_all_feedback(client, customer_token, seed_product):
    # Add feedback for pagination test
    for i in range(3):
        client.post(
            "/feedback",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "product_id": seed_product.id,
                "rating": 5,
                "comment": f"Feedback {i}",
            },
        )

    response = client.get("/feedback?page=1&per_page=2")
    assert response.status_code == 200
    data = response.get_json()
    assert "feedback" in data
    assert len(data["feedback"]) <= 2  # pagination test


def test_delete_feedback(client, app, customer_token, seed_product):
    # Create feedback to delete
    response = client.post(
        "/feedback",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={
            "product_id": seed_product.id,
            "rating": 3,
            "comment": "Temporary feedback",
        },
    )
    feedback_id = response.get_json()["feedback"]["id"]

    # Delete it
    response = client.delete(
        f"/feedback/{feedback_id}",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert response.status_code == 200
    assert response.get_json()["msg"] == "Feedback deleted successfully"
