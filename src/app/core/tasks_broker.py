from functools import cache

from taskiq_nats import PullBasedJetStreamBroker
from taskiq_nats.result_backend import NATSObjectStoreResultBackend

from app.core.settings import settings


@cache
def get_task_broker() -> PullBasedJetStreamBroker:
    task_broker = PullBasedJetStreamBroker(
        servers=[settings.NATS.URL],
    ).with_result_backend(
        result_backend=NATSObjectStoreResultBackend(
            servers=[settings.NATS.URL],
        ),
    )
    return task_broker


broker = get_task_broker()


