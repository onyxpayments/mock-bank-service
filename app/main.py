"""Application entrypoint."""

from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="OnyxPay Mock Bank Service")

app.include_router(router)
