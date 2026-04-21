import asyncio

from loguru import logger

from app.core.tasks_broker import get_task_broker

broker = get_task_broker()


@broker.task
async def debug_task(value: int):
    logger.info('Execute example task...')
    await asyncio.sleep(1)
    return value * 2
