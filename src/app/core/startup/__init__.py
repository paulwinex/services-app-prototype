from contextlib import asynccontextmanager
from typing import AsyncGenerator

import taskiq_fastapi
from fastapi import FastAPI

from app.core.events import get_event_router
from app.core.startup import init_db
from app.core.startup.init_callbacks import init_callback_modules
from app.core.startup.init_tasks import init_task_modules
from app.core.tasks_broker import get_task_broker


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    task_broker = get_task_broker()
    if not task_broker.is_worker_process:
        taskiq_fastapi.init(task_broker, "app.main:app")
        # init nats broker (for events)
        event_router = get_event_router()
        await event_router.broker.start()
        # load callbacks
        init_callback_modules(app)
        # init database
        await init_db.init_database()
        # load task modules (without starting broker - only worker should start it)
        init_task_modules(app)

    yield
    if not task_broker.is_worker_process:
        await event_router.broker.stop()
