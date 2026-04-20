from functools import cache

from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker

from app.core.settings import settings


@cache
def get_task_broker() -> RedisStreamBroker:
    result_backend = RedisAsyncResultBackend(
        redis_url=settings.REDIS.URL,
    )
    task_broker = RedisStreamBroker(
        settings.REDIS.URL,
    ).with_result_backend(
        result_backend=result_backend,
    )
    return task_broker


broker = get_task_broker()


