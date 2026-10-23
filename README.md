# Student Management System

A runnable microservices-based student management application using React/Vite, FastAPI, SQLAlchemy, Pydantic v2, SQLite, JWT, and HTTPX.

## Architecture

- `frontend`: React SPA, communicates only with the API gateway.
- `api-gateway`: forwards `/auth`, `/students`, and `/courses` requests to their services, forwards authorization, and normalizes upstream errors.
- `auth-service`: registration, login, password hashing, JWT creation and `/auth/me`.
- `student-service`: student CRUD with unique email validation.
- `course-service`: course CRUD and student enrollment. Enrollment records live in the course service database; student existence is checked through the student service.
- Each service owns a separate SQLite database and creates tables at startup.

## Requirements

- Python 3.11 or newer
- Node.js 20 or newer and npm
- Four available local ports: 8000, 8001, 8002, 8003, plus frontend 5173

## Setup

Open five terminals from the project root. Copy each `.env.example` to `.env` in its respective directory and adjust values if needed. Do not commit `.env` files. For production, set a long random `JWT_SECRET` and use HTTPS.

### 1. Auth service

```bash
cd auth-service
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Copy .env.example to .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

### 2. Student service

```bash
cd student-service
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Copy .env.example to .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8002
```

### 3. Course service

```bash
cd course-service
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Copy .env.example to .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8003
```

### 4. API gateway

```bash
cd api-gateway
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Copy .env.example to .env
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Frontend

```bash
cd frontend
npm install
# Copy .env.example to .env
npm run dev
```

Open `http://localhost:5173`. Each FastAPI service exposes Swagger UI at `/docs`: gateway `http://localhost:8000/docs`, auth `http://localhost:8001/docs`, student `http://localhost:8002/docs`, and course `http://localhost:8003/docs`.

## Environment variables

Each service has its own `.env.example`:

- Auth: `DATABASE_URL`, `JWT_SECRET`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`.
- Student: `DATABASE_URL`, `JWT_SECRET`, `JWT_ALGORITHM`.
- Course: `DATABASE_URL`, `JWT_SECRET`, `JWT_ALGORITHM`, `STUDENT_SERVICE_URL`.
- Gateway: service URLs, `FRONTEND_ORIGIN`, `REQUEST_TIMEOUT_SECONDS`.
- Frontend: `VITE_API_URL`.

Use the same `JWT_SECRET` and `JWT_ALGORITHM` in auth, student, and course services. Gateway validates protected requests by calling `/auth/me` at the auth service before forwarding. Service URLs are configured in environment files.

## API walkthrough

1. Register: `POST http://localhost:8000/auth/register` with `{"email":"admin@example.com","password":"YourSecurePassword123","full_name":"Admin User"}`.
2. Login: `POST http://localhost:8000/auth/login` with email and password. Copy `access_token` from the response.
3. Create a course: `POST /courses` with `Authorization: Bearer TOKEN` and `{"name":"Python Development","description":"Backend development course","department":"CSE"}`.
4. Create a student: `POST /students` with `{"name":"Rahul Kumar","email":"rahul@example.com","phone":"9876543210","department":"CSE","course":"Python Development"}`.
5. Enroll the student: `POST /courses/1/students/1` (replace IDs with actual IDs).
6. List enrollments: `GET /courses/1/students`.
7. Test update and delete using the returned IDs. The frontend offers forms and confirmation dialogs for these operations.

## Error behavior

- `400` for invalid state transitions such as duplicate enrollment.
- `401` for missing/invalid authentication.
- `404` for missing routes or records.
- `409` for unique-email conflicts.
- `422` for schema validation errors.
- `503` when an upstream service cannot be reached.
- `504` when an upstream service times out.

## Postman

Import `postman/collection.json`. Set collection variables `baseUrl` (default `http://localhost:8000`) and `token`. Run Register and Login, then copy the returned token into the `token` variable for protected requests.

## Suggested commit messages

- `chore: scaffold student management microservices`
- `feat(auth): add registration login and JWT validation`
- `feat(students): implement validated student CRUD`
- `feat(courses): add course CRUD and enrollment endpoints`
- `feat(gateway): route requests and normalize upstream errors`
- `feat(frontend): add protected student and course management UI`
- `docs: add setup guide and Postman collection`

## Notes

This project is designed for local development. Before production use, add rate limiting, refresh-token rotation, database migrations, structured observability, stronger role-based authorization, TLS, and deployment-specific secret management.
