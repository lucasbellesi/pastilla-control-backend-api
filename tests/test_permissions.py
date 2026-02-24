from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app


def unique_email(prefix: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}_{ts}@example.com"


def register_and_get_token(client: TestClient, prefix: str) -> str:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": unique_email(prefix),
            "full_name": "Permissions User",
            "password": "secret123",
            "role": "PATIENT",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def create_medication(client: TestClient, token: str, name: str = "Med") -> int:
    response = client.post(
        "/api/v1/medications/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": name,
            "dosage_amount": "1",
            "dosage_unit": "tablet",
            "notes": None,
            "is_active": True,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_medications_are_isolated_per_user() -> None:
    client = TestClient(app)

    token_a = register_and_get_token(client, "perm_a")
    token_b = register_and_get_token(client, "perm_b")

    med_a = create_medication(client, token_a, name="A-only")

    list_b = client.get(
        "/api/v1/medications/",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert list_b.status_code == 200
    assert all(item["id"] != med_a for item in list_b.json())

    update_b = client.put(
        f"/api/v1/medications/{med_a}",
        headers={"Authorization": f"Bearer {token_b}"},
        json={
            "name": "hijack",
            "dosage_amount": "2",
            "dosage_unit": "tablet",
            "notes": "not owner",
            "is_active": True,
        },
    )
    assert update_b.status_code == 404

    delete_b = client.delete(
        f"/api/v1/medications/{med_a}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert delete_b.status_code == 404


def test_schedule_creation_and_listing_are_owner_scoped() -> None:
    client = TestClient(app)

    token_a = register_and_get_token(client, "sched_a")
    token_b = register_and_get_token(client, "sched_b")

    med_a = create_medication(client, token_a, name="A med")
    med_b = create_medication(client, token_b, name="B med")

    create_for_a = client.post(
        "/api/v1/schedules/",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "medication_id": med_a,
            "type": "DAILY",
            "time_of_day": "08:00",
            "days_of_week_mask": 0,
            "interval_hours": None,
            "timezone_id": "UTC",
            "grace_minutes": 30,
            "is_active": True,
        },
    )
    assert create_for_a.status_code == 201
    schedule_a = create_for_a.json()["id"]

    create_b_on_a_med = client.post(
        "/api/v1/schedules/",
        headers={"Authorization": f"Bearer {token_b}"},
        json={
            "medication_id": med_a,
            "type": "DAILY",
            "time_of_day": "08:00",
            "days_of_week_mask": 0,
            "interval_hours": None,
            "timezone_id": "UTC",
            "grace_minutes": 30,
            "is_active": True,
        },
    )
    assert create_b_on_a_med.status_code == 404

    create_for_b = client.post(
        "/api/v1/schedules/",
        headers={"Authorization": f"Bearer {token_b}"},
        json={
            "medication_id": med_b,
            "type": "DAILY",
            "time_of_day": "09:00",
            "days_of_week_mask": 0,
            "interval_hours": None,
            "timezone_id": "UTC",
            "grace_minutes": 30,
            "is_active": True,
        },
    )
    assert create_for_b.status_code == 201
    schedule_b = create_for_b.json()["id"]

    list_a = client.get(
        "/api/v1/schedules/",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert list_a.status_code == 200
    ids_a = {item["id"] for item in list_a.json()}
    assert schedule_a in ids_a
    assert schedule_b not in ids_a

    list_b = client.get(
        "/api/v1/schedules/",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert list_b.status_code == 200
    ids_b = {item["id"] for item in list_b.json()}
    assert schedule_b in ids_b
    assert schedule_a not in ids_b
