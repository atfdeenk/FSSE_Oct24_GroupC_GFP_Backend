import json
import pytest
from route.subscription_route import subscription_bp
from services.subscription_services import SubscriptionService


def test_subscribe_success(client, monkeypatch):
    # Mock send_welcome_email to avoid sending real emails
    def mock_send_welcome_email(email):
        return True

    monkeypatch.setattr(
        SubscriptionService, "subscribe", lambda email: mock_send_welcome_email(email)
    )

    response = client.post(
        "/subscribe",
        data=json.dumps({"email": "test@example.com"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Subscription successful. Welcome email sent."


def test_subscribe_missing_email(client):
    response = client.post(
        "/subscribe", data=json.dumps({}), content_type="application/json"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_subscribe_invalid_email(monkeypatch, client):
    # Mock subscribe to raise ValueError for invalid email
    def mock_subscribe(email):
        raise ValueError("Email is required")

    monkeypatch.setattr(SubscriptionService, "subscribe", mock_subscribe)

    response = client.post(
        "/subscribe", data=json.dumps({"email": ""}), content_type="application/json"
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_subscribe_email_send_failure(monkeypatch, client):
    # Mock subscribe to raise Exception simulating email send failure
    def mock_subscribe(email):
        raise Exception("Failed to send email")

    monkeypatch.setattr(SubscriptionService, "subscribe", mock_subscribe)

    response = client.post(
        "/subscribe",
        data=json.dumps({"email": "test@example.com"}),
        content_type="application/json",
    )
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
