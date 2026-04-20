#!/bin/bash

worker_count=${APP_WORKER_COUNT:-1}

echo "Start workers [$worker_count]..."
exec taskiq worker \
    --workers $worker_count \
    --fs-discover \
    --app-dir app/modules \
    app.core.tasks_broker:broker
