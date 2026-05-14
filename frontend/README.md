# Student Management System Frontend

![HTML](https://img.shields.io/badge/HTML-5-E34F26?logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS-3-1572B6?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-Vanilla-F7DF1E?logo=javascript&logoColor=111827)
![Nginx](https://img.shields.io/badge/Nginx-Static%20Hosting-009639?logo=nginx&logoColor=white)

This folder contains the static frontend for the Student Management System. It is built with plain HTML, CSS, and vanilla JavaScript, and it is deployed in Docker using Nginx. The UI connects directly to the FastAPI backend at `http://localhost:8000` and provides the login, dashboard, student management, profile, and monitoring screens used in the project.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Markup | HTML |
| Styling | CSS |
| Interactivity | Vanilla JavaScript |
| Local token storage | `localStorage` |
| Deployment | Docker, Nginx |
| Backend API | FastAPI at `http://localhost:8000` |

## Features

- Login page.
- Register page.
- JWT token storage in `localStorage`.
- Role-based UI for admin and student users.
- Admin dashboard with student statistics cards.
- Student list table.
- Search, department, status, GPA min, and GPA max filters.
- Pagination using `skip` and `limit`.
- Create student form.
- View student details modal.
- Edit student form using `PATCH` requests.
- Delete student action.
- Profile section for the authenticated user.
- Monitoring section for API metrics.
- Direct integration with the FastAPI backend endpoints.

## Folder Structure

```text
frontend/
├── index.html
├── styles.css
├── app.js
├── Dockerfile
├── nginx.conf
└── README.md
```

## Screens and Pages

The UI is organized into the following screens:

- Login screen for existing users.
- Register screen for new student users.
- Dashboard screen with role-based content.
- Students screen for admin management.
- Profile screen for the current user.
- Monitoring screen for API health and metrics.

The page also uses modal dialogs and forms for creating, viewing, editing, and deleting student records.

## How It Connects to the Backend

The frontend talks to the FastAPI API using `fetch` calls in `app.js`.

- Base URL: `http://localhost:8000`
- Tokens are sent as `Authorization: Bearer <access_token>`.
- Login stores `access_token` and `token_type` in `localStorage`.
- The app loads the current user from `GET /users/me` after login.
- Admin-only UI sections are shown only when the authenticated user has the admin role.

Backend endpoints used by the frontend include:

- `POST /auth/login`
- `POST /auth/register`
- `GET /users/me`
- `GET /users/`
- `GET /students/stats/summary`
- `GET /students/`
- `GET /students/{id}`
- `POST /students/`
- `PATCH /students/{id}`
- `DELETE /students/{id}`
- `GET /students/me`
- `GET /monitoring/metrics`

## Authentication Flow

1. The user logs in through the login screen.
2. The frontend sends credentials to `POST /auth/login`.
3. On success, the frontend stores `access_token` and `token_type` in `localStorage`.
4. The token is attached to protected API requests as a Bearer token.
5. The app calls `GET /users/me` to determine the current role.
6. The UI switches between admin and student views based on that role.

Important behavior:

- `POST /auth/register` creates student users only.
- Student profile access is driven by the backend’s authenticated user context.
- Student updates use `PATCH`, not `PUT`.

## Admin Workflow

Admin users can access the full management interface:

- View dashboard statistics from `GET /students/stats/summary`.
- Open the students table.
- Search and filter students by name, university ID, department, status, and GPA range.
- Paginate student results.
- Create new student records using an existing `user_id`.
- View student details in a modal.
- Edit student records.
- Delete student records.
- Open the monitoring section and view the metrics payload.

## Student Workflow

Student users see a restricted interface:

- Log in and reach the dashboard.
- View their profile information from `GET /users/me`.
- View their linked student record from `GET /students/me`.
- Access only the parts of the UI allowed by their role.

## API Configuration

The main API base URL is configured in `app.js`:

```text
http://localhost:8000
```

If the backend runs elsewhere, update the `API_BASE` constant in `app.js`.

When deployed with Docker Compose, the frontend is served at:

```text
http://localhost:3000
```

The frontend Docker image copies `index.html`, `styles.css`, and `app.js` into Nginx and serves the static app on port 80 inside the container.

## Run with Docker Compose from the Root Project

From the repository root, start the full stack:

```bash
docker compose up -d --build
```

Useful Docker commands:

```bash
docker compose logs -f frontend
docker compose restart frontend
docker compose down
```

After the stack is running, open the app at:

```text
http://localhost:3000
```

## Run Manually Without Docker

This frontend does not require a build step. You can run it in any of the following ways:

1. Open `index.html` directly in a browser.
2. Use VS Code Live Server.
3. Use a simple static server.

Examples:

```bash
# Serve the folder with Python
python -m http.server 3000
```

If you use Live Server, make sure the backend CORS origins allow the Live Server address.

## CORS Notes

If the frontend origin is not allowed by the backend, API requests may fail in the browser.

- For Docker, the backend should allow `http://localhost:3000`.
- For Live Server, you may need to add `http://127.0.0.1:5500` or `http://localhost:5500` to `BACK_END_ALLOWED_ORIGINS` in the backend environment file.
- Restart the backend after changing CORS settings.

## Important Browser Note

Opening `index.html` with `file://` may cause browser or CORS problems. It is better to use Docker or Live Server.

## Troubleshooting

- If the app cannot reach the API, confirm the backend is running on `http://localhost:8000`.
- If you see CORS errors, update `BACK_END_ALLOWED_ORIGINS` in the backend configuration.
- If the login works but protected screens fail, make sure the token is still present in `localStorage`.
- If student actions fail, check whether the current user is an admin or whether the backend allows the requested operation.
- If Docker changes are not visible, rebuild and restart the frontend container.
- If the page looks blank when opened with `file://`, switch to Docker or a local static server.

## Notes for University Submission

- This frontend is intentionally simple and standards-based: HTML, CSS, vanilla JavaScript, and Nginx.
- Do not describe it as a React, Vue, Next.js, Tailwind, or other framework-based app.
- Include screenshots of the login, dashboard, students, profile, and monitoring screens if needed for presentation.
- The Dockerized version is the best option for a clean demo.
- Make sure the backend and frontend URLs are both working before submission.
