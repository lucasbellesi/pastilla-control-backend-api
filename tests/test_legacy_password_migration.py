from datetime import datetime, timezone

from fastapi.testclient import TestClient
from passlib.hash import pbkdf2_sha256

from app.db.session import SessionLocal
from app.main import app
from app.models.enums import UserRole
from app.models.user import User


def unique_email(prefix: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}_{ts}@example.com"


def test_login_rehashes_legacy_pbkdf2_password_to_bcrypt() -> None:
    email = unique_email("legacy")
    plain_password = "secret123"
    legacy_hash = pbkdf2_sha256.hash(plain_password)

    db = SessionLocal()
    try:
        user = User(
            email=email,
            full_name="Legacy User",
            hashed_password=legacy_hash,
            role=UserRole.PATIENT,
        )
        db.add(user)
        db.commit()
    finally:
        db.close()

    client = TestClient(app)
    login = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": plain_password},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]

    db = SessionLocal()
    try:
        updated = db.query(User).filter(User.email == email).first()
        assert updated is not None
        assert updated.hashed_password.startswith("$2")
        assert not updated.hashed_password.startswith("$pbkdf2-sha256$")
    finally:
        db.close()
