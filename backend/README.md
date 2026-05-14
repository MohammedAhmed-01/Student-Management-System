# Student Management System API

![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-Pytest-0A9EDC?logo=pytest&logoColor=white)

A professional FastAPI backend for the Student Management System. This API handles authentication, role-based access control, student management, Redis-backed caching, monitoring, migration management, and automated testing for a university student management workflow.

## Backend Architecture

The backend follows a modular FastAPI structure:

- `app/main.py` creates the FastAPI application, registers middleware, exception handlers, and routers.
- `app/core/` contains configuration, dependencies, and security-related helpers.
- `app/db/` manages the SQLAlchemy base, session, and initialization logic.
- `app/models/` defines the database models for users and students.
- `app/schemas/` contains Pydantic schemas for request and response validation.
- `app/routes/` contains the API route groups for auth, users, and students.
- `app/cache/` provides Redis access and cache management.
- `app/middlewares/` includes request logging middleware.
- `app/monitoring/` exposes metrics and a simple HTML dashboard.
- `app/utils/` includes password hashing, JWT helpers, and logging utilities.

Request flow is straightforward: a client sends a request, FastAPI validates it with Pydantic, authentication and role dependencies are applied, the endpoint reads or writes PostgreSQL through SQLAlchemy, and Redis is used for cached student detail lookups when available.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Runtime | Python 3.12 |
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Validation | Pydantic |
| Database | PostgreSQL |
| Cache | Redis |
| Authentication | JWT bearer tokens |
| Password hashing | bcrypt |
| Testing | Pytest |
| Containerization | Docker |

## Features

- User registration and login.
- JWT access token generation.
- Password hashing.
- Role-based access control.
- Admin-only user and student management endpoints.
- Student create, read, update, and delete operations.
- Student self-profile access.
- Advanced student filtering by name, university ID, department, status, and GPA range.
- Pagination using `skip` and `limit`.
- Redis cache for student detail records.
- Cache invalidation after create, update, and delete operations.
- Audit logging for important CRUD actions.
- Validation error handling.
- Database integrity error handling.
- Monitoring metrics and dashboard endpoints.
- Alembic database migrations.
- Pytest-based automated tests.

## Folder Structure

```text
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   └── security.py
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── init_db.py
│   ├── models/
│   │   ├── user.py
│   │   └── student.py
│   ├── schemas/
│   │   ├── auth.py
│   │   └── student.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── users.py
│   │   └── students.py
│   ├── cache/
│   │   ├── redis_client.py
│   │   └── cache_manager.py
│   ├── middlewares/
│   │   └── logging_middleware.py
│   ├── monitoring/
│   │   ├── dashboard.py
│   │   └── metrics.py
│   └── utils/
│       ├── hashing.py
│       ├── jwt.py
│       └── logger.py
├── alembic/
├── scripts/
│   ├── seed_data.py
│   └── test_cache_performance.py
├── tests/
│   ├── test_admin_users.py
│   └── test_students.py
├── Dockerfile
├── requirements.txt
├── .env.example
└── alembic.ini
```

## Environment Variables

The backend loads settings from `backend/.env` using `python-dotenv`. Copy `backend/.env.example` to `backend/.env` and adjust the values for your environment.

| Variable | Purpose | Example |
| --- | --- | --- |
| `DATABASE_URL` | PostgreSQL connection string used by SQLAlchemy and Alembic. Required. | `postgresql+psycopg://postgres:password@localhost:5432/student_management` |
| `REDIS_URL` | Redis connection string used by the cache layer. | `redis://localhost:6379/0` |
| `LOG_LEVEL` | Application logging level. | `INFO` |
| `CACHE_DEFAULT_TTL_SECONDS` | Default Redis cache TTL in seconds. Must be greater than 0. | `60` |
| `APP_NAME` | Application title shown in the FastAPI docs. | `Student Management API` |
| `SECRET_KEY` | JWT signing secret. Required. Use a strong random value in production. | `change-me` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token lifetime in minutes. Must be greater than 0. | `30` |
| `JWT_ALGORITHM` | JWT signing algorithm. | `HS256` |
| `BACK_END_ALLOWED_ORIGINS` | Comma-separated CORS origins. Defaults to the frontend origin. | `http://localhost:3000` |
| `SEED_USER_EMAIL` | Optional seed user email used by `scripts/seed_data.py`. | `student@example.com` |
| `SEED_USER_PASSWORD` | Optional seed user password used by `scripts/seed_data.py`. | `password` |
| `SEED_USER_ROLE` | Optional seed user role used by `scripts/seed_data.py`. | `student` |
| `SEED_STUDENT_NAME` | Optional seed student name used by `scripts/seed_data.py`. | `Sample Student` |
| `SEED_STUDENT_GPA` | Optional seed student GPA used by `scripts/seed_data.py`. | `3.5` |
| `SEED_STUDENT_DEPARTMENT` | Optional seed student department used by `scripts/seed_data.py`. | `Computer Science` |

## Run with Docker Compose from the Root Project

From the repository root, start the full stack:

```bash
docker compose up -d --build
```

Useful follow-up commands:

```bash
docker compose logs -f api
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed_data.py
docker compose exec api pytest
docker compose down
```

### Backend Docker Startup Behavior

The backend Dockerfile already runs:

```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

That means the container applies migrations first and then starts the API server automatically.

## Run Backend Manually Without Docker

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

On macOS or Linux, activate the virtual environment with:

```bash
source .venv/bin/activate
```

## Alembic Migrations

Apply the current database schema:

```bash
alembic upgrade head
```

Create a new migration after changing models:

```bash
alembic revision --autogenerate -m "describe your changes"
```

If you are using Docker Compose, run migrations inside the API container:

```bash
docker compose exec api alembic upgrade head
```

## Seed Sample Data

The repository includes a seed script at `backend/scripts/seed_data.py`.

Run it manually:

```bash
python scripts/seed_data.py
```

Run it inside Docker Compose:

```bash
docker compose exec api python scripts/seed_data.py
```

This script is intended to create or update sample admin and student records for local development and demonstrations.

## Testing

Run the test suite locally from the backend folder:

```bash
pytest
```

Run the tests in Docker Compose:

```bash
docker compose exec api pytest
```

The existing test files cover user management and student behavior through the API.

## Authentication

Authentication is implemented with JWT bearer tokens.

1. A user registers through `POST /auth/register` or logs in through `POST /auth/login`.
2. On successful login, the API returns an access token and token type.
3. The client sends the token as `Authorization: Bearer <token>` on protected requests.
4. The backend resolves the current user with dependency injection and checks the stored role for authorization.

Important behavior:

- `POST /auth/register` creates a student user.
- `POST /auth/login` returns a JWT access token.
- Protected routes use role-aware dependencies for admin-only or authenticated-user access.

## Role Permissions

| Role | Permissions |
| --- | --- |
| Anonymous | Can register and log in only. |
| Authenticated user | Can access `/users/me`, `GET /students/me`, and allowed student detail endpoints where permitted. |
| Student | Can view their own user profile and their own student profile; can update only permitted fields where the route allows it. |
| Admin | Can manage users and students, list all students, create users, view student statistics, and access monitoring data. |

## API Endpoints

| Method | Endpoint | Purpose | Access |
| --- | --- | --- | --- |
| GET | `/` | Root response confirming the API is running. | Public |
| POST | `/auth/register` | Register a new user. | Public |
| POST | `/auth/login` | Log in and receive a JWT token. | Public |
| GET | `/users/me` | Get the current user profile. | Authenticated |
| GET | `/users/` | List all users. | Admin only |
| POST | `/users/` | Create a user. | Admin only |
| PUT | `/users/me/email` | Update the current user email. | Authenticated |
| PUT | `/users/me/password` | Update the current user password. | Authenticated |
| DELETE | `/users/{user_id}` | Delete a user. | Admin only |
| POST | `/students/` | Create a student record. | Authenticated |
| GET | `/students/` | List students with filters and pagination. | Admin only |
| GET | `/students/me` | Get the current user’s student profile. | Authenticated |
| GET | `/students/{student_id}` | Get a student by ID. | Admin or owner |
| PATCH | `/students/{student_id}` | Update a student record. | Admin or owner |
| DELETE | `/students/{student_id}` | Delete a student record. | Admin only |
| GET | `/students/stats/summary` | Return student statistics summary. | Admin only |
| GET | `/monitoring/metrics` | Return API metrics as JSON. | Public |
| GET | `/monitoring/dashboard` | Return the HTML monitoring dashboard. | Public |
| GET | `/docs` | Swagger UI. | Public |
| GET | `/redoc` | ReDoc documentation. | Public |

## Redis Caching

The backend uses Redis for cached student detail lookups.

- Cached records use keys like `students:detail:{student_id}`.
- The cache layer prefers Redis and falls back to an in-memory backend if Redis is unavailable.
- Student create, update, and delete operations invalidate the relevant detail key and the `students:list` prefix.
- The cache TTL comes from `CACHE_DEFAULT_TTL_SECONDS` and defaults to 60 seconds.

This improves repeated access to student detail pages while keeping write operations consistent.

## Monitoring

The backend includes lightweight monitoring built into the API.

- `app/middlewares/logging_middleware.py` records request timing and attaches response-time metadata.
- `app/monitoring/metrics.py` collects total requests, total errors, endpoint averages, and error rates.
- `GET /monitoring/metrics` returns the current metrics snapshot as JSON.
- `GET /monitoring/dashboard` returns a simple HTML dashboard that refreshes automatically.

The dashboard is useful for quick local validation and demonstrations during university submission.

## Troubleshooting

- If the API fails to start, confirm that `DATABASE_URL` and `SECRET_KEY` are set in `backend/.env`.
- If the database schema is missing, run `alembic upgrade head` or `docker compose exec api alembic upgrade head`.
- If the frontend cannot call the API, make sure `BACK_END_ALLOWED_ORIGINS` includes the frontend origin and restart the backend.
- If Redis is unavailable, the cache layer can fall back to in-memory behavior, but local Redis should still be running for normal full-stack testing.
- If authentication fails, verify that the JWT token is being sent in the `Authorization` header.
- If tests fail because the database is stale, reset the environment with `docker compose down -v` and rebuild the stack.
- If you need to inspect runtime behavior, use `docker compose logs -f api`.

## Notes for University Submission

- The API is designed to be demonstrated with Docker Compose and Swagger UI.
- Include sample `.env` values only; do not commit secrets.
- Seed data can be generated for demos with `scripts/seed_data.py`.
- The monitoring dashboard and statistics endpoint are useful for showing operational features during presentation.
