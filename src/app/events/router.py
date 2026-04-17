from functools import cache, wraps

from faststream.nats.fastapi import NatsRouter
from pydantic import BaseModel

from app.core.settings import get_settings


@cache
def get_event_router() -> NatsRouter | None:
    settings = get_settings()
    return NatsRouter(
        servers=[settings.EVENTS.URL],
        schema_url="/asyncapi",
        include_in_schema=True,
    )



def event(event_name: str):
    def decorator(func):
        if not get_settings().EVENTS.ENABLE:
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
