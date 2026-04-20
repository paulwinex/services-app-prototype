from functools import cache
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.settings import settings


@cache
def get_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=ZoneInfo(settings.STATE.TIMEZONE))
    return scheduler
