from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core import init_db
from app.events.router import get_event_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # init nats broker
    router = get_event_router()
    await router.broker.connect()
    # setup_callbacks()
    # init database
    await init_db.init_database()
    yield


