import asyncio
import httpx
from fastapi import APIRouter, BackgroundTasks
from app.api.schemas import AuthorizationRequest, AuthorizationResponse

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


ORCHESTRATOR_CALLBACK_URL = (
    "http://payment-orchestrator-service:8001/provider-callbacks/mock-bank"
)


async def send_callback_later(request: AuthorizationRequest):
    await asyncio.sleep(5)

    callback_payload = {
        "transaction_id": request.transaction_id,
        "provider_transaction_id": f"mock_{request.transaction_id}",
        "status": "APPROVED",
        "message": "Mock bank payment approved asynchronously",
    }

    callback_url = f"{ORCHESTRATOR_CALLBACK_URL}/{request.transaction_id}"

    async with httpx.AsyncClient() as client:
        await client.post(callback_url, json=callback_payload, timeout=10)


@router.post("/authorize", response_model=AuthorizationResponse)
def authorize_payment(
    request: AuthorizationRequest,
    background_tasks: BackgroundTasks,
) -> AuthorizationResponse:

    background_tasks.add_task(send_callback_later, request)

    return AuthorizationResponse(
        transaction_id=request.transaction_id,
        provider_transaction_id=f"mock_{request.transaction_id}",
        status="PENDING",
        message="Mock bank authorization pending",
    )
