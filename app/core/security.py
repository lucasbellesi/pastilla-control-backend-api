from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


LEGACY_PBKDF2_SHA256_PREFIX = "$pbkdf2-sha256$"


def is_legacy_password_hash(hashed_password: str) -> bool:
    return hashed_password.startswith(LEGACY_PBKDF2_SHA256_PREFIX)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if is_legacy_password_hash(hashed_password):
        from passlib.hash import pbkdf2_sha256

        return pbkdf2_sha256.verify(plain_password, hashed_password)

    encoded_password = plain_password.encode("utf-8")
    encoded_hash = hashed_password.encode("utf-8")
    return bcrypt.checkpw(encoded_password, encoded_hash)


def get_password_hash(password: str) -> str:
    encoded_password = password.encode("utf-8")
    return bcrypt.hashpw(encoded_password, bcrypt.gensalt()).decode("utf-8")


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
