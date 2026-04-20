from contextlib import asynccontextmanager
from typing import AsyncGenerator

import taskiq_fastapi
from fastapi import FastAPI
from loguru import logger

from app.core.events import get_event_router
from app.core.scheduler import get_scheduler
from app.core.settings import settings
from app.core.startup import init_db
from app.core.startup.init_callbacks import init_callback_modules
from app.core.startup.init_scheduled_tasks import init_scheduler_tasks
from app.core.startup.init_tasks import init_task_modules
from app.core.tasks_broker import get_task_broker


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    task_broker = get_task_broker()
    if not task_broker.is_worker_process:
        taskiq_fastapi.init(task_broker, "app.main:app")
        # init nats broker (for events)
        logger.info('Start event router')
        event_router = get_event_router()
        await event_router.broker.start()
        # load callbacks
        logger.info('Load callbacks from modules')
        init_callback_modules(app)
        # init database
        await init_db.init_database(app)
        # load task modules (without starting broker - only worker should start it)
        logger.info('Loading background tasks from modules')
        init_task_modules(app)
        # scheduler
        if settings.STATE.ENABLE_SCHEDULER:
            logger.info('Load scheduler tasks from modules')
            init_scheduler_tasks(app)
            logger.info('Start scheduler')
            get_scheduler().start()

    yield
    if not task_broker.is_worker_process:
        logger.info('Stop event router')
        await event_router.broker.stop()
        if settings.STATE.ENABLE_SCHEDULER:
            logger.info('Stop scheduler')
            get_scheduler().shutdown()
            logger.info('Start event router')
            await event_router.broker.stop()
