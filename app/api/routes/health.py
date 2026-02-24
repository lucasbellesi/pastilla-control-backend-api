from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import SessionLocal


router = APIRouter()


def _check_db() -> None:
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    finally:
        db.close()


@router.get("/live")
def live_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready_check() -> dict[str, str]:
    _check_db()
    return {"status": "ok", "db": "ok"}


@router.get("/")
def health_check() -> dict[str, str]:
    _check_db()

    return {"status": "ok", "db": "ok"}
