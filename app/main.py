"""Application entrypoint."""

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.routes import router

app = FastAPI(title="OnyxPay Mock Bank Service")

app.include_router(health_router)
app.include_router(router)
