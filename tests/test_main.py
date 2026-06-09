from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("app.api.routes.asyncio.sleep", new_callable=AsyncMock)
@patch("app.api.routes.httpx.AsyncClient.post", new_callable=AsyncMock)
def test_authorize_returns_pending_and_sends_callback(
    mock_post,
    mock_sleep,
):
    payload = {
        "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
        "amount": 10000,
        "currency": "COP",
        "customer": {
            "first_name": "Juan",
            "last_name": "Bello",
            "personal_id": "123456789",
        },
    }

    response = client.post("/authorize", json=payload)
    print(response.json())

    assert response.status_code == 200

    data = response.json()

    assert data["transaction_id"] == payload["transaction_id"]
    assert data["provider_transaction_id"] == f"mock_{payload['transaction_id']}"
    assert data["status"] == "PENDING"

    mock_sleep.assert_called_once_with(5)

    mock_post.assert_called_once()

    url = mock_post.call_args.args[0]
    body = mock_post.call_args.kwargs["json"]

    assert url.endswith(f"/provider-callbacks/mock-bank/{payload['transaction_id']}")

    assert body["provider_transaction_id"] == f"mock_{payload['transaction_id']}"
    assert body["status"] == "APPROVED"


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
