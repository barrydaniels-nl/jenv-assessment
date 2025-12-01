# Flask TODO API

JenV assessment REST API for managing todos with JWT authentication.


## Tech Stack

| Library | Purpose | Why |
|---------|---------|-----|
| **Flask** | Web framework | Simple, stays out of the way. No magic. |
| **SQLModel** | ORM | One model for both database and validation. SQLAlchemy + Pydantic in one. |
| **Pydantic** | Validation | Handles request/response validation. Good error messages. |
| **flask-jwt-extended** | Auth | JWT with refresh tokens built in. |
| **Alembic** | Migrations | The standard for SQLAlchemy. |
| **Gunicorn** | WSGI Server | Battle-tested. |
| **uv** | Package manager | Way faster than pip. |
| **pytest** | Testing | Good fixtures, readable tests. |
| **ruff** | Linting | Fast. Replaces flake8, isort, etc. |
| **black** | Formatting | Ends style debates. |

## Project Structure

```
app/
    __init__.py           # Application factory
    api/v1/               # API version 1
        routes/           # Endpoint handlers
            auth.py       # Authentication endpoints
            health.py     # Health check
            todos.py      # Todo CRUD endpoints
    core/
        config.py         # Configuration management
        database.py       # Database connection
    migrations/           # Alembic migrations
    models/               # SQLModel database models
    schemas/              # Pydantic request/response schemas
    services/             # Business logic layer
tests/
    conftest.py           # Shared test fixtures
    test_routes/          # Integration tests
    test_services/        # Unit tests
.github/workflows/        # CI/CD pipeline
Dockerfile
docker-compose.yaml
openapi.yaml              # API specification
```

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### Local Development

```bash
# Clone and enter directory
git clone git@github.com:barrydaniels-nl/jenv-assessment.git
cd jenv-assessment

# Install dependencies
uv sync --dev

# Copy environment file
cp .env.example .env

# Run migrations
uv run alembic upgrade head

# Start development server
uv run python run.py
```

The API will be available at `http://localhost:5050`.

### Docker

```bash
# Build and run
docker-compose up --build

# Or run in background
docker-compose up -d
```

Docker automatically runs migrations on startup via `entrypoint.sh`.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_DEBUG` | `0` | Enable debug mode (1 for development) |
| `SECRET_KEY` | `dev-secret-key` | Flask secret key |
| `DATABASE_URL` | `sqlite:///./app.db` | Database connection string |
| `JWT_SECRET_KEY` | `dev-jwt-secret-key` | JWT signing key |
| `JWT_ACCESS_TOKEN_EXPIRES` | `900` | Access token expiry (seconds) |
| `JWT_REFRESH_TOKEN_EXPIRES` | `604800` | Refresh token expiry (seconds) |
| `CORS_ORIGINS` | `*` | Allowed origins (comma-separated or `*`) |

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/health` | Health check | No |
| `POST` | `/api/v1/auth/register` | Register new user | No |
| `POST` | `/api/v1/auth/login` | Login, get tokens | No |
| `POST` | `/api/v1/auth/refresh` | Refresh access token | Refresh token |
| `GET` | `/api/v1/auth/me` | Get current user | Access token |
| `GET` | `/api/v1/todos` | List todos (paginated) | Access token |
| `POST` | `/api/v1/todos` | Create todo | Access token |
| `GET` | `/api/v1/todos/{id}` | Get todo | Access token |
| `PUT` | `/api/v1/todos/{id}` | Update todo | Access token |
| `DELETE` | `/api/v1/todos/{id}` | Delete todo | Access token |
| `POST` | `/api/v1/todos/{id}/toggle` | Toggle completion | Access token |

### Query Parameters for List Todos

- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 10, max: 100)
- `completed` - Filter by completion status (true/false)
- `sort_by` - Field to sort by: `title`, `completed`, `priority`, `due_date`, `created_at`, `updated_at` (default: `created_at`)
- `order` - Sort order: `asc` or `desc` (default: `desc`)

## API Documentation

Interactive API documentation is available at `/docs` when the server is running.

The OpenAPI specification is in `openapi.yaml`.

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_services/test_auth_service.py

# Run with coverage
uv run pytest --cov=app
```

## Code Quality

### Pre-commit Hooks

```bash
# Install hooks (run once)
uv run pre-commit install

# Run manually
uv run pre-commit run --all-files
```

### Manual Linting

```bash
uv run ruff check .
uv run ruff format .
uv run black .
```

## CI/CD

GitHub Actions runs on every push and PR to `main`:

1. **pre-commit** - Runs all pre-commit hooks
2. **test** - Runs the full test suite

## Architecture Decisions

### Application Factory Pattern

App is created via `create_app()` in `app/__init__.py`. Makes testing easier since you can spin up fresh instances with different configs.

### Service Layer

Business logic lives in `app/services/`, not in route handlers. Routes deal with HTTP stuff, services deal with business rules. Easier to test this way.

### SQLModel for Models

SQLModel = SQLAlchemy + Pydantic. Define your model once, use it for both database and validation.

### JWT with Refresh Tokens

Access tokens expire in 15 minutes, refresh tokens in 7 days. Short-lived access tokens mean less damage if one gets stolen. Refresh tokens keep users from having to log in constantly.

### User Data Isolation

Every todo query filters by `user_id`. You can only touch your own data. This check happens in the service layer, not just the routes.

### Test Organization

- `test_services/` - Unit tests for business logic
- `test_routes/` - Integration tests, full request/response
- `conftest.py` - Shared fixtures

Tests run against an in-memory SQLite database. Fast and isolated.

### Configuration

All config comes from environment variables. Defaults are set for local dev so it just works out of the box. See `app/core/config.py`.
