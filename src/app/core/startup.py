from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from app.core import init_db
# from loguru import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # init db migrations (DEV MODE)
    # init database
    await init_db.init_database()
    # start scheduler
    # init bg task broker
    yield
    # stop and wait scheduler
    # stop broker
