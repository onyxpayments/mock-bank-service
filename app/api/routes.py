import asyncio
import logging

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends

from app.api.schemas import AuthorizationRequest, AuthorizationResponse
from app.application.scenario_selector import ScenarioSelector
from app.domain.scenarios import CallbackScenario
from app.infrastructure.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

scenario_selector = ScenarioSelector(settings.scenario_probabilities)


def select_scenario() -> CallbackScenario:
    return scenario_selector.choose()


async def send_callback(
    request: AuthorizationRequest,
    status: str,
) -> None:
    callback_payload = {
        "provider_transaction_id": f"mock_{request.transaction_id}",
        "status": status,
        "message": f"Mock bank payment {status.lower()} asynchronously",
    }

    callback_url = f"{settings.orchestrator_callback_url}/{request.transaction_id}"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            callback_url,
            json=callback_payload,
            timeout=10,
        )
        response.raise_for_status()


async def send_callback_after(
    request: AuthorizationRequest,
    status: str,
    delay_seconds: float,
) -> None:
    await asyncio.sleep(delay_seconds)
    await send_callback(request, status)


async def send_duplicate_callback(request: AuthorizationRequest) -> None:
    await asyncio.sleep(settings.approved_delay_seconds)
    await send_callback(request, "APPROVED")
    await asyncio.sleep(settings.duplicate_delay_seconds)
    await send_callback(request, "APPROVED")


@router.post("/authorize", response_model=AuthorizationResponse)
async def authorize_payment(
    request: AuthorizationRequest,
    background_tasks: BackgroundTasks,
    scenario: CallbackScenario = Depends(select_scenario),
) -> AuthorizationResponse:
    logger.info(
        "Selected callback scenario %s for transaction %s",
        scenario.value,
        request.transaction_id,
    )

    if scenario == CallbackScenario.APPROVED_AFTER_5:
        background_tasks.add_task(
            send_callback_after,
            request,
            "APPROVED",
            settings.approved_delay_seconds,
        )
    elif scenario == CallbackScenario.DECLINED_AFTER_20:
        background_tasks.add_task(
            send_callback_after,
            request,
            "DECLINED",
            settings.declined_delay_seconds,
        )
    elif scenario == CallbackScenario.DUPLICATE_CALLBACK:
        background_tasks.add_task(send_duplicate_callback, request)
    elif scenario == CallbackScenario.CALLBACK_BEFORE_RESPONSE:
        await send_callback(request, "APPROVED")

    return AuthorizationResponse(
        transaction_id=request.transaction_id,
        provider_transaction_id=f"mock_{request.transaction_id}",
        status="PENDING",
        message="Mock bank authorization pending",
    )
