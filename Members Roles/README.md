# 🎓 Student Management System

## 📌 Overview

This project is a backend system built using **FastAPI** to manage university students.
It includes authentication, role-based access control, student CRUD operations, filtering, pagination, caching, logging, testing, and a simple frontend (GUI).

---

## 🚀 Features

* User registration & login (JWT authentication)
* Role-based access (Admin / Student)
* Full CRUD operations for students
* Filtering (department, GPA)
* Pagination support
* Student profile access restriction
* Audit logging for updates
* Redis caching
* Logging & monitoring
* API testing with pytest
* Simple GUI (frontend)

---

## 🛠 Tech Stack

* FastAPI
* SQLAlchemy
* MSSQL
* Redis
* Pytest
* HTML / CSS / JavaScript (Frontend)
* Docker

---

## 📂 Project Structure

```
student-management-system/
│
├── app/
│   ├── main.py                # Entry point of the FastAPI application
│   │
│   ├── core/                 # Core configurations
│   │   ├── config.py         # Environment variables & settings
│   │   ├── database.py       # Database connection setup
│   │   ├── security.py       # JWT, password hashing
│   │   ├── dependencies.py   # Shared dependencies (auth, roles)
│   │   └── logging_config.py # Logging configuration
│   │
│   ├── models/               # Database models (SQLAlchemy)
│   │   ├── user.py           # User model
│   │   ├── student.py        # Student model
│   │   └── audit_log.py      # Audit log model
│   │
│   ├── schemas/              # Pydantic schemas (validation)
│   │   ├── auth.py           # Login & register schemas
│   │   ├── user.py           # User schemas
│   │   ├── student.py        # Student schemas
│   │   └── audit_log.py      # Audit log schemas
│   │
│   ├── routers/              # API routes (endpoints)
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── users.py          # User-related endpoints
│   │   ├── students.py       # Student CRUD endpoints
│   │   └── monitoring.py     # Health & monitoring endpoints
│   │
│   ├── services/             # Business logic layer
│   │   ├── auth_service.py   # Authentication logic
│   │   ├── student_service.py# Student logic
│   │   ├── audit_service.py  # Audit logging logic
│   │   ├── cache_service.py  # Redis caching logic
│   │   └── monitoring_service.py # Monitoring logic
│   │
│   ├── repositories/         # Database access layer
│   │   ├── user_repository.py
│   │   ├── student_repository.py
│   │   └── audit_repository.py
│   │
│   ├── middleware/           # Middleware (request/response handling)
│   │   └── request_logger.py # Logs API requests & responses
│   │
│   └── utils/                # Helper utilities
│       ├── pagination.py     # Pagination logic
│       └── filters.py        # Filtering logic
│
├── tests/                    # Test cases (pytest)
│   ├── test_auth.py
│   ├── test_students.py
│   ├── test_roles.py
│   ├── test_filtering.py
│   ├── test_pagination.py
│   └── conftest.py           # Shared test configuration
│
├── frontend/                 # Simple GUI (HTML/CSS/JS or React)
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── profile.html
│   │
│   ├── css/
│   │   └── styles.css
│   │
│   ├── js/
│   │   ├── api.js           # API calls (fetch/axios)
│   │   ├── auth.js          # Login/Register logic
│   │   ├── students.js      # Students operations
│   │   └── utils.js         # Helper functions
│
├── docker/                   # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
├── .gitignore
└── README.md
```

---

# 👥 Team Members & Responsibilities

---

## 🧑‍💻 Member 1 — Setup, Database, Docker, Documentation

### Responsibilities:

* Setup project structure
* Configure FastAPI project
* Setup database connection
* Create models (User, Student, AuditLog)
* Create Dockerfile & docker-compose
* Write README

### Deliverables:

* `core/database.py`
* `models/`
* `Dockerfile`
* `docker-compose.yml`
* `README.md`

### Branch:

`feature/setup-database-docker-docs`

---

## 🧑‍💻 Member 2 — Authentication & Security

### Responsibilities:

* User registration
* User login
* Password hashing
* JWT token generation & validation
* Protect routes
* Role-based authorization

### Deliverables:

* `auth.py`
* `security.py`
* `auth_service.py`

### Branch:

`feature/auth-jwt-security`

---

## 🧑‍💻 Member 3 — Student CRUD & Profile

### Responsibilities:

* Create student
* Get all students
* Get student by ID
* Update student
* Delete student
* Student can view/update own profile only

### Deliverables:

* `students.py`
* `student_service.py`
* `student schemas`

### Branch:

`feature/student-crud-profile`

---

## 🧑‍💻 Member 4 — Filtering & Pagination

### Responsibilities:

* Filtering by department
* Filtering by GPA
* Combine filters
* Add pagination
* Optimize queries

### Deliverables:

* `filters.py`
* `pagination.py`
* Updated GET endpoints

### Branch:

`feature/filtering-pagination-query`

---

## 🧑‍💻 Member 5 — Caching, Logging, Monitoring

### Responsibilities:

* Integrate Redis caching
* Cache GET requests
* Cache invalidation
* Add logging (requests, errors, auth events)
* Build monitoring endpoints

### Deliverables:

* `cache_service.py`
* `logging_config.py`
* `monitoring.py`

### Branch:

`feature/cache-logging-monitoring`

---

## 🧑‍💻 Member 6 — Audit, Testing, GUI

### Responsibilities:

* Audit logging for updates
* Store old/new values
* Create tests using pytest
* Test all system features
* Build simple frontend (GUI)

### Deliverables:

* `audit_service.py`
* `tests/`
* `frontend/`

### Branch:

`feature/testing-gui-docs-audit`

---

## ⚙️ How to Run

### 1) Clone the repo

```
git clone <your-repo-link>
cd student-management-system
```

### 2) Run with Docker

```
docker-compose up --build
```

### 3) Open API Docs

```
http://127.0.0.1:8000/docs
```

---

## 🧪 Run Tests

```
pytest
```

---

## 🔥 Notes

* Each member must work on their own branch
* Use pull requests for merging
* Follow clean and modular code structure
* Make sure all features are tested

---
