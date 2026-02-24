# Backend Pastilla Control

[![CI](https://github.com/lucasbellesi/pastilla-control-backend-api/actions/workflows/ci.yml/badge.svg)](https://github.com/lucasbellesi/pastilla-control-backend-api/actions/workflows/ci.yml)

API REST for PastillaControl using FastAPI + PostgreSQL.

## Stack

- FastAPI
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
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

4. PostgreSQL connection (host machine):

- Host: `127.0.0.1`
- Port: `5433`
- Database: `pastilla_control`
- User: `pastilla`
- Password: `pastilla`

## Local run (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Core endpoints (MVP)

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login` (OAuth2 form: `username`, `password`)
- `GET /api/v1/medications`
- `POST /api/v1/medications`
- `GET /api/v1/schedules`
- `POST /api/v1/schedules`
- `GET /api/v1/health`
- `GET /api/v1/health/live`
- `GET /api/v1/health/ready`

## Notes

- Docker startup runs `alembic upgrade head` before booting the API.
- API responses include `X-Request-ID` and HTTP request logs include the same id.
- `APP_ENV` values other than `dev` require a non-default `JWT_SECRET_KEY`.
- This scaffold is intentionally minimal and production-safe defaults should be hardened:
  - rotate secrets
  - add refresh tokens
  - add RBAC and relationship checks for family members
  - add worker service for escalation processing
