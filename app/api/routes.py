"""API routes for the mock bank service."""

from fastapi import APIRouter
from app.api.schemas import AuthorizationRequest, AuthorizationResponse

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/authorize", response_model=AuthorizationResponse)
def authorize_payment(request: AuthorizationRequest) -> AuthorizationResponse:
    return AuthorizationResponse(
        transaction_id=request.transaction_id,
        provider_transaction_id=f"mock_{request.transaction_id}",
        status="APPROVED",
        message="Mock bank authorization approved",
    )
