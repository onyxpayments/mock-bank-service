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
        "country": "CO",
    }

    response = client.post("/authorize", json=payload)

    assert response.status_code == 200

    body = response.json()

    assert body["transaction_id"] == "trx_123"
    assert body["provider_transaction_id"] == "mock_trx_123"
    assert body["status"] == "APPROVED"
    assert body["message"] == "Mock bank authorization approved"


def test_authorize_rejects_missing_required_field():
    payload = {
        "transaction_id": "trx_123",
        "amount": 10000,
        "currency": "COP",
    }

    response = client.post("/authorize", json=payload)

    assert response.status_code == 422
