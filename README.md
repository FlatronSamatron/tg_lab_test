# Expedition Management Service

Backend service for managing expeditions. Built with FastAPI, PostgreSQL, and WebSockets.

## Stack

- FastAPI, SQLAlchemy 2.0 (async), Alembic, PostgreSQL, JWT (cookies), WebSockets, Docker

## Setup

Create a `.env` file:

```env
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=db
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5433/db
ACCESS_TOKEN_EXPIRE_MINUTES=1440
SECRET_KEY=your_secret_key_at_least_32_characters_long
ALGORITHM=HS256
```

## Running with Docker

```bash
docker-compose up --build
```

Then apply migrations:

```bash
docker-compose exec app alembic upgrade head
```

API available at `http://localhost:8000`. Swagger UI at `http://localhost:8000/docs`.

## Running locally

```bash
docker-compose up postgres       # start database
alembic upgrade head             # apply migrations
uv run uvicorn app.main:app --reload
```

## Tests

```bash
pytest -v
```

Tests use an in-memory SQLite database, no external dependencies required.

## WebSocket testing

1. Login via Swagger at `http://127.0.0.1:8000/docs` — browser saves the `acces_token` cookie.
2. Open `http://127.0.0.1:8000/ws_test`, enter expedition ID and connect.
3. Trigger events via Swagger (invite member, change status) — events appear in real time.

Event format:
```json
{"event": "member_invited", "user_id": 1}
{"event": "member_confirmed", "user_id": 1}
{"event": "expedition_status", "status": "active"}
```
