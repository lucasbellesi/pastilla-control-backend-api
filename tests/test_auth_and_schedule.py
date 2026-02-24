from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app


def unique_email(prefix: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}_{ts}@example.com"


def register_user(client: TestClient, email: str, password: str = "secret123") -> dict:
    return client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Test User",
            "password": password,
            "role": "PATIENT",
        },
    ).json()


def create_medication(client: TestClient, token: str) -> int:
    response = client.post(
        "/api/v1/medications/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Ibuprofeno",
            "dosage_amount": "1",
            "dosage_unit": "tablet",
            "notes": "test",
            "is_active": True,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_register_is_idempotent_for_same_credentials() -> None:
    client = TestClient(app)
    email = unique_email("idempotent")

    first = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Idempotent User",
            "password": "secret123",
            "role": "PATIENT",
        },
    )
    assert first.status_code == 200
    assert first.json()["access_token"]

    second_same_password = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Idempotent User",
            "password": "secret123",
            "role": "PATIENT",
        },
    )
    assert second_same_password.status_code == 200
    assert second_same_password.json()["access_token"]

    third_different_password = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Idempotent User",
            "password": "different-pass",
            "role": "PATIENT",
        },
    )
    assert third_different_password.status_code == 400
    assert third_different_password.json()["detail"] == "Email already exists"


def test_login_uses_oauth2_password_form() -> None:
    client = TestClient(app)
    email = unique_email("oauth")
    password = "secret123"
    register_user(client, email=email, password=password)

    login = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]
    assert login.json()["token_type"] == "bearer"


def test_schedule_validation_rules() -> None:
    client = TestClient(app)
    email = unique_email("schedule")
    register = register_user(client, email=email)
    token = register["access_token"]
    medication_id = create_medication(client, token)

    weekly_missing_days = client.post(
        "/api/v1/schedules/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "medication_id": medication_id,
            "type": "WEEKLY",
            "time_of_day": "09:00",
            "days_of_week_mask": 0,
            "interval_hours": None,
            "timezone_id": "UTC",
            "grace_minutes": 30,
            "is_active": True,
        },
    )
    assert weekly_missing_days.status_code == 422
    assert "days_of_week_mask must be > 0" in str(weekly_missing_days.json())

    interval_missing_hours = client.post(
        "/api/v1/schedules/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "medication_id": medication_id,
            "type": "INTERVAL",
            "time_of_day": "09:00",
            "days_of_week_mask": 0,
            "interval_hours": None,
            "timezone_id": "UTC",
            "grace_minutes": 30,
            "is_active": True,
        },
    )
    assert interval_missing_hours.status_code == 422
    assert "interval_hours is required when type is INTERVAL" in str(
        interval_missing_hours.json()
    )

    invalid_time_timezone = client.post(
        "/api/v1/schedules/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "medication_id": medication_id,
            "type": "DAILY",
            "time_of_day": "9",
            "days_of_week_mask": 0,
            "interval_hours": None,
            "timezone_id": "Bad/Timezone",
            "grace_minutes": 30,
            "is_active": True,
        },
    )
    assert invalid_time_timezone.status_code == 422
    assert "time_of_day must use HH:MM format" in str(invalid_time_timezone.json())
    assert "timezone_id must be a valid IANA timezone" in str(invalid_time_timezone.json())
