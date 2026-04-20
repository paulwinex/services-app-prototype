from functools import cache

from faststream.nats.fastapi import NatsRouter

from app.core.settings import settings, Settings


@cache
def get_event_router() -> NatsRouter | None:
    return NatsRouter(
        servers=[settings.NATS.URL],
        schema_url="/asyncapi",
        include_in_schema=True,
    )



