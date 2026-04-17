#!/bin/bash

alembic upgrade head

exec uvicorn app.main:create_app --host 0.0.0.0 --port 8000 ${DEBUG:+--reload}
