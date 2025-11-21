.PHONY: help install dev build up down restart logs clean test migrate upgrade downgrade

# Variables
PYTHON := python3.13
VENV := .venv
DOCKER_COMPOSE := docker compose

help:
	@echo "Available commands:"
	@echo "  make install          - Create virtual environment and install dependencies"
	@echo "  make dev              - Run the app locally with hot reload"
	@echo "  make build            - Build Docker images"
	@echo "  make up               - Start all Docker containers"
	@echo "  make down             - Stop all Docker containers"
	@echo "  make restart          - Restart Docker containers"
	@echo "  make logs             - View logs from all containers"
	@echo "  make logs-backend     - View backend container logs"
	@echo "  make logs-celery      - View celery worker logs"
	@echo "  make shell-backend    - Open shell in backend container"
	@echo "  make shell-db         - Open PostgreSQL shell"
	@echo "  make clean            - Remove containers, volumes, and images"
	@echo "  make test             - Run tests"
	@echo "  make migrate          - Create a new migration"
	@echo "  make upgrade          - Apply migrations"
	@echo "  make downgrade        - Rollback migrations"
	@echo "  make format           - Format code with black"
	@echo "  make lint             - Lint code with ruff"

# Local Development
install:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
	@echo "Virtual environment created. Activate it with: source $(VENV)/bin/activate"

dev:
	$(VENV)/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Docker Commands
build:
	$(DOCKER_COMPOSE) build --no-cache

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

restart:
	$(DOCKER_COMPOSE) restart

logs:
	$(DOCKER_COMPOSE) logs -f

logs-backend:
	$(DOCKER_COMPOSE) logs -f backend

logs-celery:
	$(DOCKER_COMPOSE) logs -f celery_worker

logs-db:
	$(DOCKER_COMPOSE) logs -f postgres

logs-redis:
	$(DOCKER_COMPOSE) logs -f redis

# Container Shell Access
shell-backend:
	$(DOCKER_COMPOSE) exec backend /bin/sh

shell-db:
	$(DOCKER_COMPOSE) exec postgres psql -U benedetto -d b_boutique

shell-redis:
	$(DOCKER_COMPOSE) exec redis redis-cli

# Database Migrations
migrate:
	@read -p "Enter migration message: " msg; \
	$(VENV)/bin/alembic revision --autogenerate -m "$$msg"

upgrade:
	$(VENV)/bin/alembic upgrade head

downgrade:
	$(VENV)/bin/alembic downgrade -1

# Testing
test:
	$(VENV)/bin/pytest -v

test-cov:
	$(VENV)/bin/pytest --cov=app --cov-report=html

# Code Quality
format:
	$(VENV)/bin/black app/
	$(VENV)/bin/isort app/

lint:
	$(VENV)/bin/ruff check app/

# Cleanup
clean:
	$(DOCKER_COMPOSE) down -v --rmi all
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

clean-docker:
	$(DOCKER_COMPOSE) down -v

# Database Operations
db-reset:
	$(DOCKER_COMPOSE) down -v
	$(DOCKER_COMPOSE) up -d postgres
	sleep 5
	$(MAKE) upgrade

# Health Check
health:
	@curl -s http://localhost:8000/api/v1/health | jq .

# Install development tools
install-dev:
	$(VENV)/bin/pip install black isort ruff pytest pytest-cov pytest-asyncio httpx
