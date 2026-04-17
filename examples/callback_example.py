from faststream.nats.fastapi import Logger
from loguru import logger

from app.events.router import get_event_router
from app.events.schemas import ModelEvent
from app.modules.users.schemas import UserEvent

router = get_event_router()


logger.info('Setup callbacks...')
@router.subscriber("model.*.create")
async def on_model_create(event: ModelEvent, log: Logger) -> None:
    log.info(f"Model created: {event.model_name} with id {event.object_id}")


@router.subscriber("model.*.update")
async def on_model_update(event: ModelEvent, log: Logger) -> None:
    log.info(f"Model updated: {event.model_name} with id {event.object_id}")


@router.subscriber("model.*.delete")
async def on_model_delete(event: ModelEvent, log: Logger) -> None:
    log.info(f"Model deleted: {event.model_name} with id {event.object_id}")


@router.subscriber("auth.user-logged-in")
@router.publisher("user-login-postprocess")
async def on_user_logged_in(event: UserEvent, log: Logger) -> str:
    log.info(f"User Logged In: {event.id}")
    return event.id


@router.subscriber("user-login-postprocess")
async def postprocess_logged_in_user(user_id: str, log: Logger):
    log.debug(f'🚀 USER PROCESS {user_id}')
