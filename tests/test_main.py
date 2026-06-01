"""Tests for mock bank service."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_authorize_returns_approved_response():
    payload = {
        "transaction_id": "trx_123",
        "amount": 10000,
        "currency": "COP",
        "customer": {
            "first_name": "Juan",
            "last_name": "Bello",
            "personal_id": "123456789",
        },
    }

    response = client.post("/authorize", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["transaction_id"] == "trx_123"
    assert body["provider_transaction_id"] == "mock_trx_123"
    assert body["status"] == "APPROVED"
    assert body["message"] == "Mock bank authorization approved"

    response = client.post("/authorize", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["transaction_id"] == "trx_123"
    assert body["provider_transaction_id"] == "mock_trx_123"
    assert body["status"] == "APPROVED"
    assert body["message"] == "Mock bank authorization approved"


def test_authorize_rejects_missing_customer():
    payload = {
        "transaction_id": "trx_123",
        "amount": 10000,
        "currency": "COP",
    }

    response = client.post("/authorize", json=payload)

    assert response.status_code == 422


def test_authorize_rejects_missing_customer_personal_id():
    payload = {
        "transaction_id": "trx_123",
        "amount": 10000,
        "currency": "COP",
        "customer": {
            "first_name": "Juan",
            "last_name": "Bello",
        },
    }

    response = client.post("/authorize", json=payload)

    assert response.status_code == 422
