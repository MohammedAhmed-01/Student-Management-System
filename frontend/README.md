# Student Management System — Static Frontend

Vanilla **HTML**, **CSS**, and **JavaScript** UI for the FastAPI Student Management API. No frameworks, build tools, or npm packages.

## Technologies

- HTML5
- CSS3 (custom properties, responsive layout)
- JavaScript (ES5-friendly `function` / `var` style for broad browser support)

## Backend URL

Default API base URL: **http://localhost:8000**

Change the `API_BASE` constant at the top of `app.js` if your server runs elsewhere.

## How to run the frontend

1. Start the FastAPI backend so it listens on `http://localhost:8000`.
2. Open `index.html` in a browser **or** use **VS Code Live Server** (or any static file server).

### CORS

The API reads allowed origins from `BACK_END_ALLOWED_ORIGINS` (see backend `.env`). The default in code is often `http://localhost:3000`. If the browser blocks requests, add your frontend origin (for example `http://127.0.0.1:5500` for Live Server) to that environment variable, comma-separated, and restart the API.

## Main features

- **Login** — `POST /auth/login`, JWT stored in `localStorage` (`access_token`, `token_type`).
- **Register** — `POST /auth/register` (creates **student** users only; the backend ignores admin for this route).
- **Dashboard** — Admin: stats from `GET /students/stats/summary` plus a monitoring snapshot from `GET /monitoring/metrics`. Student: welcome overview only.
- **Students (admin)** — List `GET /students/` with filters (`department`, `gpa_min`, `gpa_max`, `status`, `search`) and pagination (`skip`, `limit`).
- **CRUD** — Create `POST /students/`, read `GET /students/{id}`, update **`PATCH /students/{id}`** (the API does not expose `PUT`), delete `DELETE /students/{id}`.
- **Profile** — `GET /users/me`; students also load `GET /students/me` when available.
- **Monitoring** — Metrics JSON and a link to `http://localhost:8000/monitoring/dashboard`.

## Important notes

- The **backend must be running** before the UI can load data.
- **Student create** requires a valid **`user_id`** (existing user). Admins pick a user from the list loaded via `GET /users/`.
- **Updates** use **`PATCH /students/{id}`**, matching the FastAPI routes (not `PUT`).
- List GPA filters use query names **`gpa_min`** and **`gpa_max`** (not `min_gpa` / `max_gpa`).
- Opening `index.html` via `file://` may hit **CORS** restrictions; using Live Server on an allowed origin is recommended.

## Files in this folder

- `index.html` — Layout, auth views, dashboard, students, profile, monitoring, modals.
- `styles.css` — Theme, layout, components.
- `app.js` — API client, auth, role-based UI, tables, forms.
- `README.md` — This file.
- `Dockerfile` / `nginx.conf` — Optional container deployment for this static site.
