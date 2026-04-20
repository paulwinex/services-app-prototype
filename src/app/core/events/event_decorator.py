from functools import wraps

from loguru import logger
from pydantic import BaseModel

from app.core.events import get_event_router
from app.core.settings import settings


def event(event_name: str):
    def decorator(func):
        if not settings.STATE.ENABLE_EVENTS:
            logger.debug('Events is disabled')
            # fast stream events is disabled
            async def nothing(*args, **kwargs):
                pass
            return nothing

        @wraps(func)
        async def wrapper(*args, **kwargs):
            data = await func(*args, **kwargs)
            broker = get_event_router().broker
            if isinstance(data, BaseModel):
                data = data.model_dump(mode='json')
            await broker.publish(data, subject=event_name)

        return wrapper
    return decorator
