from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from app.api.routes import select_scenario
from app.domain.scenarios import CallbackScenario
from app.main import app

client = TestClient(app)

VALID_PAYLOAD = {
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "amount": 10000,
    "currency": "COP",
    "notification_url": "https://merchant.example/webhooks/payments",
    "customer": {
        "first_name": "Juan",
        "last_name": "Bello",
        "personal_id": "123456789",
    },
}


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides.clear()


def force_scenario(scenario: CallbackScenario) -> None:
    app.dependency_overrides[select_scenario] = lambda: scenario


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_liveness_returns_alive():
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_startup_returns_started():
    response = client.get("/health/startup")

    assert response.status_code == 200
    assert response.json() == {"status": "started"}


def test_readiness_returns_ready():
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


@pytest.mark.parametrize(
    ("scenario", "delay", "callback_status"),
    [
        (CallbackScenario.APPROVED_AFTER_5, 5, "APPROVED"),
        (CallbackScenario.DECLINED_AFTER_20, 20, "DECLINED"),
    ],
)
def test_delayed_callback_scenarios(
    scenario,
    delay,
    callback_status,
):
    force_scenario(scenario)

    with (
        patch(
            "app.api.routes.asyncio.sleep",
            new_callable=AsyncMock,
        ) as mock_sleep,
        patch(
            "app.api.routes.send_callback",
            new_callable=AsyncMock,
        ) as mock_callback,
    ):
        response = client.post("/authorize", json=VALID_PAYLOAD)

    assert response.status_code == 200
    assert response.json()["status"] == "PENDING"
    mock_sleep.assert_awaited_once_with(delay)
    assert mock_callback.await_args.args[1] == callback_status


def test_duplicate_callback_scenario_sends_the_same_callback_twice():
    force_scenario(CallbackScenario.DUPLICATE_CALLBACK)

    with (
        patch(
            "app.api.routes.asyncio.sleep",
            new_callable=AsyncMock,
        ) as mock_sleep,
        patch(
            "app.api.routes.send_callback",
            new_callable=AsyncMock,
        ) as mock_callback,
    ):
        response = client.post("/authorize", json=VALID_PAYLOAD)

    assert response.status_code == 200
    assert [call.args[0] for call in mock_sleep.await_args_list] == [5, 1]
    assert mock_callback.await_count == 2
    assert {call.args[1] for call in mock_callback.await_args_list} == {"APPROVED"}


@patch("app.api.routes.httpx.AsyncClient.post", new_callable=AsyncMock)
def test_callback_before_response_sends_callback_without_transaction_id(
    mock_post,
):
    force_scenario(CallbackScenario.CALLBACK_BEFORE_RESPONSE)
    mock_post.return_value = httpx.Response(
        status_code=200,
        request=httpx.Request("POST", "http://orchestrator/callback"),
    )

    response = client.post("/authorize", json=VALID_PAYLOAD)

    assert response.status_code == 200
    assert response.json()["status"] == "PENDING"
    mock_post.assert_awaited_once()
    callback_body = mock_post.await_args.kwargs["json"]
    assert "transaction_id" not in callback_body
    assert callback_body["status"] == "APPROVED"


def test_no_callback_scenario_does_not_schedule_delivery():
    force_scenario(CallbackScenario.NO_CALLBACK)

    with patch(
        "app.api.routes.send_callback",
        new_callable=AsyncMock,
    ) as mock_callback:
        response = client.post("/authorize", json=VALID_PAYLOAD)

    assert response.status_code == 200
    assert response.json()["status"] == "PENDING"
    mock_callback.assert_not_awaited()


def test_authorize_rejects_missing_customer():
    payload = {
        "transaction_id": "trx_123",
        "amount": 10000,
        "currency": "COP",
    }

    response = client.post("/authorize", json=payload)

    assert response.status_code == 422


def test_authorize_rejects_missing_notification_url():
    payload = dict(VALID_PAYLOAD)
    payload.pop("notification_url")

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
