# 🎓 Student Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![Pytest](https://img.shields.io/badge/Tests-Pytest-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)

Professional full-stack university student management system built with FastAPI, PostgreSQL, Redis, and a static HTML/CSS/JavaScript frontend. The project supports secure JWT-based authentication, role-based access control, student CRUD operations, Redis-backed caching, audit-style application logging, and custom monitoring routes.

## Features

- JWT authentication with user registration and login.
- Role-based access control for admin and student users.
- Admin management for users and students.
- Student profile access with partial self-updates where allowed.
- Student CRUD operations with search, department, status, GPA range, skip/limit pagination.
- Redis cache for student detail lookups, with invalidation after writes.
- Application logging for create, update, and delete actions.
- API validation and consistent error handling.
- Custom monitoring metrics and HTML dashboard.
- Dockerized backend, frontend, PostgreSQL, Redis, and Redis Commander.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | FastAPI, Python 3.12, SQLAlchemy 2, Pydantic, Alembic |
| Authentication | JWT with python-jose, password hashing with bcrypt |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Frontend | Static HTML, CSS, Vanilla JavaScript served by Nginx |
| Testing | Pytest |
| Deployment | Docker, Docker Compose |
| Monitoring | Custom FastAPI metrics and dashboard routes |
| Redis UI | Redis Commander |

## Architecture Overview

The backend follows a modular FastAPI structure:

- `routes/` handles request/response flow and authorization.
- `schemas/` validates input and output payloads.
- `models/` defines SQLAlchemy database entities.
- `db/` manages sessions, base models, and initialization.
- `cache/` provides Redis access and cache management.
- `middlewares/` adds logging middleware.
- `monitoring/` exposes operational metrics and a dashboard.
- `utils/` contains hashing, JWT, and logging helpers.

Request flow is straightforward: the frontend calls the FastAPI API, JWT tokens are attached as Bearer tokens, the API validates permissions, reads or writes PostgreSQL, and uses Redis for cached student data when available.

## Project Structure

```text
Student-Management-System/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routes/
│   │   ├── cache/
│   │   ├── middlewares/
│   │   ├── monitoring/
│   │   └── utils/
│   ├── alembic/
│   ├── scripts/
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   ├── Dockerfile
│   └── nginx.conf
├── docs/
├── docker-compose.yml
└── README.md
```

## Run with Docker

1. Make sure Docker and Docker Compose are installed.
2. From the project root, start the full stack:

```bash
docker compose up --build
```

The backend container runs database migrations automatically before starting Uvicorn with:

```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

## Stop Docker

```bash
docker compose down
```

To stop the stack and remove volumes as well:

```bash
docker compose down -v
```

## Rebuild Containers

```bash
docker compose up -d --build
```

## View Logs

```bash
docker compose logs -f api
```

Useful companion command:

```bash
docker compose ps
```

## Run Backend Manually

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

On Windows PowerShell, use:

```powershell
.venv\Scripts\Activate.ps1
```

## Run Frontend Manually

The frontend is a static site with no npm dependencies. Serve the `frontend/` folder with any static server, for example:

```bash
cd frontend
python -m http.server 3000
```

Then open `http://localhost:3000` in your browser.

## Environment Variables

Backend configuration is loaded from `backend/.env` and the provided example file.

| Variable | Purpose | Example / Default |
| --- | --- | --- |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg://postgres:password@localhost:5432/student_management` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `LOG_LEVEL` | Application log level | `INFO` |
| `CACHE_DEFAULT_TTL_SECONDS` | Default cache TTL in seconds | `60` |
| `APP_NAME` | FastAPI app title | `Student Management API` |
| `SECRET_KEY` | JWT signing secret | Set a strong random value |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiry in minutes | `30` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `BACK_END_ALLOWED_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |

Optional seed variables used by `backend/scripts/seed_data.py` are also defined in `backend/.env.example`.

## API Endpoints Summary

### Authentication

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/auth/register` | Register a new user. Public registration creates a student user. |
| POST | `/auth/login` | Log in and receive a JWT access token. |

### Users

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/users/me` | Get the authenticated user profile. |
| GET | `/users/` | List all users. Admin only. |
| POST | `/users/` | Create a user. Admin only. |
| PUT | `/users/me/email` | Update the current user email. |
| PUT | `/users/me/password` | Update the current user password. |
| DELETE | `/users/{user_id}` | Delete a user. Admin only. |

### Students

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/students/` | List students with search, department, status, GPA range, skip, and limit. Admin only. |
| POST | `/students/` | Create a student record. |
| GET | `/students/me` | Get the authenticated user’s student profile. |
| GET | `/students/{student_id}` | Get a student by ID. |
| PATCH | `/students/{student_id}` | Partially update a student record. |
| DELETE | `/students/{student_id}` | Delete a student record. Admin only. |
| GET | `/students/stats/summary` | Get student statistics summary. Admin only. |

### Monitoring

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/monitoring/metrics` | Return current API metrics as JSON. |
| GET | `/monitoring/dashboard` | Open the HTML monitoring dashboard. |

### Root

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/` | Health-style root response confirming the API is running. |

## Authentication Flow

1. Register or log in through `/auth/register` or `/auth/login`.
2. The API returns a JWT access token on successful login.
3. The frontend stores the token in `localStorage` and sends it as `Authorization: Bearer <token>`.
4. The API resolves the current user through `/users/me` and uses the user role for access control.
5. Admin users can manage users and students; student users can access their own account and student profile data.

## Default Local URLs

| Service | URL |
| --- | --- |
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Redis Commander | http://localhost:8081 |
| PostgreSQL | localhost:5433 |
| Redis | localhost:6379 |

## Testing

Run the test suite from the backend directory:

```bash
cd backend
pytest
```

If you are using Docker Compose, run:

```bash
docker compose exec api pytest
```

## Useful Docker Commands

```bash
docker compose up --build
docker compose up -d --build
docker compose down
docker compose down -v
docker compose logs -f api
docker compose ps
docker compose exec api alembic upgrade head
docker compose exec api pytest
docker compose exec api python scripts/seed_data.py
```

## Troubleshooting

- If the frontend cannot reach the API, confirm the backend is running on `http://localhost:8000` and that `BACK_END_ALLOWED_ORIGINS` includes the frontend origin.
- If database tables are missing, run `alembic upgrade head` or `docker compose exec api alembic upgrade head`.
- If a container fails during startup, check `docker compose logs -f api` for migration or connection errors.
- If port bindings fail, make sure ports `3000`, `8000`, `5433`, `6379`, and `8081` are free on your machine.
- If Redis cache behavior seems stale, remember that student detail and list caches are invalidated after student create, update, and delete operations.

## Notes for University Submission

- The backend is FastAPI-based and the frontend is intentionally static, so do not describe it as React or Next.js.
- Include your `.env` file locally, but do not commit secrets.
- The Docker Compose setup is the most reliable way to demonstrate the full stack during presentation.
- If you seed sample data, run `docker compose exec api python scripts/seed_data.py` after the services are up.
- Swagger UI and the monitoring dashboard are useful for demos because they show both the API and the operational views.

## Future Improvements

- Add richer reporting and more student analytics.
- Expand automated tests for cache invalidation and monitoring behavior.
- Add stricter validation and finer-grained field-level permissions where needed.
- Improve the monitoring dashboard with charts and historical trends.
- Add production deployment notes for a hosted environment.

## License

This project is intended for educational and university submission use.
