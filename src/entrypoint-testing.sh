#!/bin/bash
set -e

echo "APPLY MIGRATIONS..."
alembic upgrade head

echo "START TESTING... $PWD"
cd /app
pytest -x -v