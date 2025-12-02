#!/bin/bash
# Run database migrations before starting the app
echo "Running database migrations..."
alembic upgrade head
echo "Migrations completed!"
