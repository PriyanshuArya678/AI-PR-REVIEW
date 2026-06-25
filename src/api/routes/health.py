from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    """Liveness check — lets you (and later, your host) confirm the app is up."""
    return {"status": "ok"}
