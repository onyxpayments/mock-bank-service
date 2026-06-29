from pydantic import BaseModel, HttpUrl
from app.domain.models import Customer


class AuthorizationRequest(BaseModel):
    transaction_id: str
    amount: float
    currency: str
    notification_url: HttpUrl

    customer: Customer


class AuthorizationResponse(BaseModel):
    transaction_id: str
    provider_transaction_id: str
    status: str
    message: str
