from datetime import datetime, timezone
from functools import wraps

from app.core.settings import get_settings


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def utcnow_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def events_enabled(func):
    if not get_settings().EVENTS.ENABLE:
        # fast stream events is disabled
        async def nothing(*args, **kwargs):
            pass
        return nothing

    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    return wrapper
