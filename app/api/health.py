from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/live")
def liveness() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/startup")
def startup() -> dict[str, str]:
    return {"status": "started"}


@router.get("/ready")
def readiness() -> dict[str, str]:
    return {"status": "ready"}
