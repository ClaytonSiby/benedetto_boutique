# B Boutique Backend API

E-commerce backend built with FastAPI, PostgreSQL, Redis, and Celery.

## Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   └── v1/           # API version 1
│   │       ├── endpoints/  # Endpoint modules
│   │       └── api.py      # API router
│   ├── core/             # Core functionality
│   │   ├── config.py     # Application settings
│   │   ├── redis.py      # Redis connection
│   │   ├── cache.py      # Cache manager
│   │   └── session.py    # Session manager
│   ├── db/               # Database
│   │   ├── base.py       # Base for models
│   │   └── session.py    # DB session
│   ├── models/           # SQLAlchemy models (to be created)
│   ├── schemas/          # Pydantic schemas (to be created)
│   ├── services/         # Business logic (to be created)
│   ├── worker/           # Celery workers
│   │   ├── celery_app.py # Celery configuration
│   │   └── tasks.py      # Background tasks
│   └── main.py           # FastAPI application
├── alembic/              # Database migrations (to be initialized)
├── alembic.ini           # Alembic configuration
├── docker-compose.yml    # Docker services
├── Dockerfile            # Container definition
├── Makefile              # Common commands
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment variables
└── .gitignore           # Git ignore rules
```

## Technology Stack

- **FastAPI 0.115.6**: Modern web framework for building APIs
- **PostgreSQL 15**: Primary database
- **Redis 7**: Caching and session storage
- **Celery 5.4.0**: Background task processing
- **SQLAlchemy 2.0.37**: Database ORM
- **Alembic 1.14.0**: Database migrations
- **Pydantic 2.10.6**: Data validation
- **psycopg 3.2.3**: PostgreSQL adapter (Python 3.13 compatible)
- **Docker**: Containerization
- **Python 3.13.9**: Runtime environment

## Prerequisites

- **Python 3.13.9** (required for local development)
- **Docker Desktop** (latest version)
- **Make** (optional, for using Makefile commands)

## Quick Start

### Option 1: Using Docker (Recommended)

The fastest way to get started:

```bash
# 1. Configure environment
cp .env.example .env

# 2. Build and start all services
make build
make up

# 3. View logs
make logs
```

Your API will be available at:
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

### Option 2: Local Development

For development with hot reload:

```bash
# 1. Create virtual environment and install dependencies
make install

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Configure environment
cp .env.example .env
# Edit .env and set local connection strings

# 4. Start services (PostgreSQL and Redis via Docker)
docker compose up -d postgres redis

# 5. Run the application locally
make dev
```

## Detailed Setup Instructions

### Docker Environment Setup

#### 1. Configure Environment Variables

```bash
cp .env.example .env
```

**Required Variables** (edit `.env`):
```env
# Database
POSTGRES_USER=benedetto
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=b_boutique

# Security
SECRET_KEY=generate_with_openssl_rand_hex_32
SESSION_SECRET_KEY=generate_with_openssl_rand_hex_32
```

Generate secure keys:
```bash
openssl rand -hex 32
```

#### 2. Build Docker Images

```bash
# Build with cache
docker compose build

# Or rebuild from scratch
make build
```

#### 3. Start All Services

```bash
# Using docker compose
docker compose up -d

# Or using Makefile
make up
```

This starts four containers:
- **benedetto_boutique_postgres** - PostgreSQL database (port 5432)
- **benedetto_boutique_redis** - Redis cache (port 6379)
- **benedetto_boutique_backend** - FastAPI application (port 8000)
- **benedetto_boutique_celery_worker** - Background task processor

#### 4. Verify Services

```bash
# Check all containers are running
docker compose ps

# View logs
make logs

# Check backend logs specifically
make logs-backend

# Health check
make health
# or
curl http://localhost:8000/api/v1/health
```

### Local Development Setup

#### 1. Install Python 3.13.9

Ensure you have Python 3.13.9 installed:
```bash
python3.13 --version
# Should output: Python 3.13.9
```

#### 2. Create Virtual Environment

```bash
# Using Makefile
make install

# Or manually
python3.13 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Configure for Local Development

Update `.env` with local connection strings:
```env
# Database (local PostgreSQL or Docker)
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432

# Redis (local Redis or Docker)
REDIS_HOST=localhost
REDIS_PORT=6379
```

#### 4. Start Required Services

You can run PostgreSQL and Redis via Docker while developing locally:

```bash
# Start only database and Redis
docker compose up -d postgres redis

# Verify they're running
docker compose ps
```

#### 5. Initialize Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Edit alembic/env.py to add:
from app.db.base import Base
target_metadata = Base.metadata

# Create initial migration
make migrate
# Enter migration message when prompted

# Apply migrations
make upgrade
```

#### 6. Run the Application

```bash
# With hot reload (recommended for development)
make dev

# Or manually
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 7. Run Celery Worker (Optional)

In a separate terminal:
```bash
source .venv/bin/activate
celery -A app.worker.celery_app worker --loglevel=info -Q emails,orders,inventory
```

## Makefile Commands

The Makefile provides convenient shortcuts for common operations:

### Development Commands
```bash
make help              # Show all available commands
make install           # Create venv and install dependencies
make dev               # Run app locally with hot reload
make install-dev       # Install development tools (black, ruff, pytest)
```

### Docker Commands
```bash
make build             # Build Docker images (no cache)
make up                # Start all containers
make down              # Stop all containers
make restart           # Restart containers
make logs              # View all logs (follow mode)
make logs-backend      # View backend logs only
make logs-celery       # View celery worker logs only
make logs-db           # View PostgreSQL logs
make logs-redis        # View Redis logs
```

### Container Access
```bash
make shell-backend     # Open shell in backend container
make shell-db          # Open PostgreSQL shell
make shell-redis       # Open Redis CLI
```

### Database Operations
```bash
make migrate           # Create new migration (prompts for message)
make upgrade           # Apply all pending migrations
make downgrade         # Rollback last migration
make db-reset          # Reset database (drops volumes and re-migrates)
```

### Code Quality
```bash
make format            # Format code with black and isort
make lint              # Lint code with ruff
make test              # Run tests with pytest
make test-cov          # Run tests with coverage report
```

### Cleanup
```bash
make clean             # Remove containers, volumes, images, and venv
make clean-docker      # Remove only Docker containers and volumes
```

### Health Check
```bash
make health            # Check API health (requires jq)
```

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
  - Interactive API explorer
  - Try out endpoints directly
  - View request/response schemas

- **ReDoc**: http://localhost:8000/redoc
  - Alternative documentation format
  - Better for reading and sharing

- **OpenAPI JSON**: http://localhost:8000/openapi.json
  - Raw OpenAPI specification
  - For API client generation

## Available Endpoints

### Health Check Endpoints
- `GET /api/v1/health/` - Basic health check
- `GET /api/v1/health/database` - Database connection status
- `GET /api/v1/health/redis` - Redis connection status

### Testing Endpoints

```bash
# Basic health check
curl http://localhost:8000/api/v1/health

# Database health
curl http://localhost:8000/api/v1/health/database

# Redis health
curl http://localhost:8000/api/v1/health/redis
```

## Database Migrations

### Creating Migrations

```bash
# Auto-generate migration from model changes
make migrate
# or
alembic revision --autogenerate -m "description"

# Create empty migration (manual)
alembic revision -m "description"
```

### Applying Migrations

```bash
# Apply all pending migrations
make upgrade
# or
alembic upgrade head

# Apply specific number of migrations
alembic upgrade +1

# Upgrade to specific revision
alembic upgrade <revision_id>
```

### Rolling Back Migrations

```bash
# Rollback last migration
make downgrade
# or
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

### Viewing Migration History

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic heads
```

## Working with Celery Tasks

### Defining Tasks

Tasks are defined in `app/worker/tasks.py`:

```python
from app.worker.celery_app import celery_app

@celery_app.task(name="send_email")
def send_email(to: str, subject: str, body: str):
    # Implementation
    pass
```

### Calling Tasks

```python
from app.worker.tasks import send_email

# Async execution
send_email.delay("user@example.com", "Subject", "Body")

# With options
send_email.apply_async(
    args=["user@example.com", "Subject", "Body"],
    countdown=60  # Execute after 60 seconds
)
```

### Monitoring Tasks

```bash
# View Celery worker logs
make logs-celery

# Access backend container to check task status
make shell-backend
python -c "from app.worker.celery_app import celery_app; print(celery_app.control.inspect().active())"
```

## Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PROJECT_NAME` | API project name | "B Boutique API" | No |
| `VERSION` | API version | "1.0.0" | No |
| `DEBUG` | Debug mode | False | No |
| `POSTGRES_USER` | PostgreSQL username | - | Yes |
| `POSTGRES_PASSWORD` | PostgreSQL password | - | Yes |
| `POSTGRES_SERVER` | PostgreSQL host | localhost | No |
| `POSTGRES_PORT` | PostgreSQL port | 5432 | No |
| `POSTGRES_DB` | Database name | b_boutique | No |
| `REDIS_HOST` | Redis host | localhost | No |
| `REDIS_PORT` | Redis port | 6379 | No |
| `REDIS_DB` | Redis database index | 0 | No |
| `REDIS_PASSWORD` | Redis password | None | No |
| `SECRET_KEY` | JWT secret key | - | Yes |
| `SESSION_SECRET_KEY` | Session encryption key | - | Yes |
| `ALGORITHM` | JWT algorithm | HS256 | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry | 30 | No |
| `SESSION_MAX_AGE` | Session duration (seconds) | 86400 | No |

## Troubleshooting

### Docker Issues

**Container won't start:**
```bash
# Check logs
make logs-backend

# Rebuild without cache
make build

# Reset everything
make clean
make build
make up
```

**Port already in use:**
```bash
# Check what's using the port
lsof -i :8000

# Stop conflicting service or change port in docker-compose.yml
```

**Database connection errors:**
```bash
# Ensure postgres is healthy
docker compose ps

# Check postgres logs
make logs-db

# Reset database
make db-reset
```

### Local Development Issues

**Import errors:**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Python version mismatch:**
```bash
# Verify Python version
python --version
# Should be 3.13.9

# Recreate venv with correct Python
rm -rf .venv
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Migration errors:**
```bash
# Check current revision
alembic current

# View migration history
alembic history

# Stamp to specific revision (if needed)
alembic stamp head
```

### Redis Connection Issues

```bash
# Test Redis connection
make shell-redis
> PING
# Should respond with PONG

# Check Redis logs
make logs-redis
```

## Development Workflow

### 1. Daily Development

```bash
# Start services
make up

# View logs in follow mode
make logs

# Make code changes (hot reload is enabled)

# When done
make down
```

### 2. Adding New Features

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes to models
# Edit app/models/...

# Create migration
make migrate

# Apply migration
make upgrade

# Test changes
make test

# Commit and push
git add .
git commit -m "Add new feature"
git push
```

### 3. Code Quality Checks

```bash
# Format code
make format

# Check linting
make lint

# Run tests
make test

# Generate coverage report
make test-cov
# View htmlcov/index.html
```

## Production Considerations

### Environment Configuration

- Use strong `SECRET_KEY` and `SESSION_SECRET_KEY`
- Set `DEBUG=False`
- Configure proper CORS origins
- Use environment-specific `.env` files
- Enable HTTPS/TLS
- Set up proper logging

### Database

- Use connection pooling
- Configure proper backup strategy
- Set up read replicas if needed
- Monitor query performance
- Enable SSL connections

### Redis

- Configure persistence (AOF/RDB)
- Set up Redis Sentinel or Cluster for HA
- Enable authentication
- Monitor memory usage

### Celery

- Scale workers based on load
- Use separate queues for different task types
- Configure task retries and timeouts
- Monitor task failures
- Set up Flower for monitoring

### Docker

- Use multi-stage builds
- Scan images for vulnerabilities
- Use specific version tags (not `latest`)
- Limit container resources
- Use Docker secrets for sensitive data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
- Open an issue on GitHub
- Contact: your-email@example.com

## Creating Database Migrations

```bash
# Auto-generate migration from models
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Running Tests

```bash
pytest
```

## Development Commands

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## Next Steps

1. Create database models in `app/models/`
2. Create Pydantic schemas in `app/schemas/`
3. Implement business logic in `app/services/`
4. Add API endpoints in `app/api/v1/endpoints/`
5. Implement authentication and authorization
6. Add external service integrations (Stripe, PayPal, SendGrid, etc.)
7. Set up monitoring with Sentry

## Environment Variables

See `.env.example` for all available configuration options.

## Docker Commands

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

## Production Considerations

- Use strong, unique values for `SECRET_KEY` and `SESSION_SECRET_KEY`
- Set `DEBUG=False` in production
- Configure proper CORS origins
- Set up SSL/TLS certificates
- Configure proper logging and monitoring
- Set resource limits in docker-compose
- Use environment-specific configuration files
- Set up database backups
- Configure Redis persistence
