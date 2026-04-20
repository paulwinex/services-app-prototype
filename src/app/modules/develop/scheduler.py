from loguru import logger

from app.core.scheduler import get_scheduler


def schedule():
    scheduler = get_scheduler()

    @scheduler.scheduled_job('interval', minutes=1,)
    async def example_scheduled_job():
        logger.info("Starting example job")
