# Backend Pastilla Control

API REST for PastillaControl using FastAPI + MariaDB.

## Stack

- FastAPI
- SQLAlchemy 2.x
- Alembic
- MariaDB
- JWT auth

## Quick start (Docker)

1. Copy env file:

```bash
cp .env.example .env
```

2. Start services:

```bash
docker compose up --build
```

3. API docs:

- http://localhost:8000/docs

## Local run (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Core endpoints (MVP)

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/medications`
- `POST /api/v1/medications`
- `GET /api/v1/schedules`
- `POST /api/v1/schedules`
- `GET /api/v1/health`

## Notes

- This scaffold is intentionally minimal and production-safe defaults should be hardened:
  - rotate secrets
  - add refresh tokens
  - add RBAC and relationship checks for family members
  - add worker service for escalation processing
