import pytest

from app.core.config import Settings


def test_allows_default_jwt_secret_in_dev() -> None:
    settings = Settings(APP_ENV="dev", JWT_SECRET_KEY="change_this_secret")
    assert settings.JWT_SECRET_KEY == "change_this_secret"


def test_rejects_default_jwt_secret_outside_dev() -> None:
    with pytest.raises(ValueError, match="JWT_SECRET_KEY must be changed"):
        Settings(APP_ENV="prod", JWT_SECRET_KEY="change_this_secret")


def test_allows_non_default_secret_outside_dev() -> None:
    settings = Settings(APP_ENV="prod", JWT_SECRET_KEY="super-secret-prod-key")
    assert settings.JWT_SECRET_KEY == "super-secret-prod-key"
