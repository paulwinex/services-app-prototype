#!/bin/bash

exec uvicorn app.main:create_app --port 8000 ${DEBUG:+--reload}
