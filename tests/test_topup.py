import os
import pytest

# Auto-remove CSV after each test run to avoid pollution
@pytest.fixture(autouse=True)
def cleanup_topup_csv():
    yield
    try:
        os.remove("topup_requests.csv")
    except FileNotFoundError:
        pass

def test_request_topup_valid(client, customer_token):
    headers = {"Authorization": f"Bearer {customer_token}"}
    response = client.post(
        "/users/me/request-topup",
        json={"amount": 50000},
        headers=headers
    )
    assert response.status_code == 200
    assert "requested" in response.json
    assert response.json["requested"]["amount"] == 50000.0

def test_request_topup_invalid_amount(client, customer_token):
    headers = {"Authorization": f"Bearer {customer_token}"}
    response = client.post(
        "/users/me/request-topup",
        json={"amount": -1000},
        headers=headers
    )
    assert response.status_code == 400
    assert response.json["msg"] == "Invalid top-up amount"

def test_admin_get_topup_requests(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/topup-requests", headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json["requests"], list)