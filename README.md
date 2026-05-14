# 🎓 Student Management System API

A scalable and production-ready full-stack system built with **FastAPI** to manage university students, featuring secure authentication, role-based access control, advanced querying, caching, logging, monitoring, testing, and a modern Next.js frontend with i18n support.

---

## 🚀 Features

* 🔐 **JWT Authentication**
  * Secure user registration & login
  * Token-based authentication

* 🛡 **Role-Based Authorization**
  * Admin: full access
  * Student: limited access (own profile only)

* 📚 **Student Management**
  * Full CRUD operations
  * Controlled profile access

* 🔍 **Advanced Querying**
  * Filter by department, GPA, level
  * Pagination support

* ⚡ **Performance Optimization**
  * Redis caching (Cache-Aside Pattern)

* 📊 **Logging & Monitoring**
  * API request & response logging
  * Error tracking
  * System health endpoints
  * Monitoring dashboard & metrics API

* 🧾 **Audit Logging**
  * Track updates with old/new values

* 🧪 **Testing**
  * Full API testing using pytest
  * Cache performance testing

* 🖥 **Frontend (GUI)**
  * Next.js interface with English & Arabic support (i18n)

---

## 🏗 Architecture Overview

The system follows a **clean modular architecture**:

* **Routes** → Handle API endpoints
* **Schemas** → Validate request & response data
* **Models** → SQLAlchemy database models
* **Cache** → Redis Cache-Aside integration
* **Core** → Configurations & security
* **Middleware** → Logging & request handling
* **Monitoring** → Metrics collection & dashboard

---

## 🛠 Tech Stack

| Layer            | Technology                                       |
| ---------------- | ------------------------------------------------ |
| Backend          | Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic    |
| Database         | PostgreSQL 16                                    |
| Cache            | Redis 7                                          |
| Authentication   | JWT (python-jose), bcrypt                        |
| Frontend         | Next.js 16, React 19, TypeScript, Tailwind CSS 4 |
| i18n             | next-intl (English & Arabic)                     |
| Testing          | Pytest                                           |
| Containerization | Docker, Docker Compose                           |

---

## 📂 Project Structure

```bash
student-management-api/
├── backend/                      # FastAPI backend
│   ├── app/                      # Application code
│   │   ├── main.py               # Application entry point
│   │   ├── core/config.py        # Settings & environment config
│   │   ├── db/                   # Database session, base, init
│   │   ├── models/               # SQLAlchemy models (User, Student)
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── routes/               # API endpoints (auth, users, students)
│   │   ├── cache/                # Redis client & cache manager
│   │   ├── middlewares/          # Logging middleware
│   │   ├── monitoring/           # Metrics & dashboard
│   │   └── utils/                # Logger utilities
│   ├── alembic/                  # Database migrations
│   ├── scripts/                  # Seed data & test scripts
│   ├── tests/                    # Pytest test suite
│   ├── Dockerfile                # Backend Docker image
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Environment variable template
│   └── alembic.ini               # Alembic configuration
├── frontend/                     # Next.js frontend application
├── docs/                         # Project documentation & API spec
├── docker-compose.yml            # Full-stack Docker orchestration
└── README.md
```

---

## ⚙️ Installation & Setup

### Prerequisites

Make sure you have the following installed:

* Git
* Docker and Docker Compose
* Node.js 18+ and npm (for manual frontend setup)

---

## 🐳 Run with Docker (Recommended)

Docker Compose will start PostgreSQL, Redis, and the FastAPI server all together.

**1. Clone the Repository**

```bash
git clone https://github.com/your-username/student-management-api.git
cd student-management-api
```

**2. Start All Services**

```bash
docker compose up --build
```

This will automatically:

* Start PostgreSQL on port 5432
* Start Redis on port 6379
* Run database migrations
* Start the API server on port 8000
* Start the frontend on port 3000

---

## 🖥 Manual Setup (Development)

### 1) Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2) Configure Environment Variables

Copy `.env.example` to `.env` and update the values:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/db_name
SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379/0
BACK_END_ALLOWED_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO
CACHE_DEFAULT_TTL_SECONDS=60
APP_NAME=Student Management API
```

### 3) Run Database Migrations

```bash
alembic upgrade head
```

### 4) Start the Backend

```bash
uvicorn app.main:app --reload
```

### 5) Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## 🔑 Default Credentials

| Role    | Email               | Password    |
| ------- | ------------------- | ----------- |
| Admin   | admin@example.com   | admin123    |
| Student | student@example.com | password123 |

> If running manually, seed the database first: `python scripts/seed_data.py`

---

## 🌐 Accessing the Application

| Service              | URL                                        |
| -------------------- | ------------------------------------------ |
| Frontend             | http://localhost:3000                      |
| API Root             | http://localhost:8000                      |
| Swagger Docs         | http://localhost:8000/docs                 |
| ReDoc                | http://localhost:8000/redoc                |
| Monitoring Dashboard | http://localhost:8000/monitoring/dashboard |
| Monitoring Metrics   | http://localhost:8000/monitoring/metrics   |

---

## 🔗 API Endpoints (Examples)

| Method | Endpoint       | Description       |
| ------ | -------------- | ----------------- |
| POST   | /auth/register | Register user     |
| POST   | /auth/login    | Login             |
| GET    | /students      | Get all students  |
| GET    | /students/{id} | Get student by ID |
| POST   | /students      | Create student    |
| PUT    | /students/{id} | Update student    |
| DELETE | /students/{id} | Delete student    |

---

## 🧪 Running Tests

```bash
cd backend

# Run all tests
pytest

# Run a specific test file
pytest tests/test_students.py

# Run cache performance test
python scripts/test_cache_performance.py
```

---

## 🗄 Alembic Migrations

```bash
cd backend

# Apply all pending migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "describe your changes"

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

---

## 🌍 Environment Variables Reference

| Variable                      | Description                        | Default / Example                        |
| ----------------------------- | ---------------------------------- | ---------------------------------------- |
| `DATABASE_URL`                | PostgreSQL connection string       | `postgresql+psycopg://user:pass@host/db` |
| `REDIS_URL`                   | Redis connection string            | `redis://localhost:6379/0`               |
| `SECRET_KEY`                  | JWT signing secret                 | *(generate a strong random string)*      |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time in minutes   | `30`                                     |
| `JWT_ALGORITHM`               | JWT signing algorithm              | `HS256`                                  |
| `BACK_END_ALLOWED_ORIGINS`    | CORS allowed origins               | `http://localhost:3000`                  |
| `LOG_LEVEL`                   | Logging level                      | `INFO`                                   |
| `CACHE_DEFAULT_TTL_SECONDS`   | Default cache TTL in seconds       | `60`                                     |
| `APP_NAME`                    | Application name shown in docs     | `Student Management API`                 |

---

## 📌 Best Practices

* Follow modular architecture
* Use environment variables for secrets
* Validate all inputs using Pydantic
* Apply role-based access strictly
* Use caching for performance optimization
* Ensure full test coverage

---

## 👥 Team Contributions

| Scope |
| ----- |
| Backend Core — project setup, database design, models, migrations, auth, CRUD endpoints |
| Caching + Logging + Monitoring — Redis integration, structured logging, monitoring dashboard |

---

## 📄 License

This project is for educational purposes.

---

## ⭐ Project Value

This project demonstrates a **real-world full-stack system design** including authentication, authorization, caching, logging, monitoring, testing, i18n, and scalable architecture — making it highly suitable for production-level learning and portfolio presentation.
