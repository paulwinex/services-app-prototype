from faststream.nats.fastapi import Logger

from app.core.events import get_event_router
from app.core.events import EntityEvent
from app.modules.users.schemas import UserEvent

router = get_event_router()


@router.subscriber("model.created")
async def on_model_create(event: EntityEvent, log: Logger) -> None:
    log.info(f"Model created: {event.model_name} with id {event.entity_id}")


@router.subscriber("model.updated")
async def on_model_update(event: EntityEvent, log: Logger) -> None:
    log.info(f"Model updated: {event.model_name} with id {event.entity_id}")


@router.subscriber("model.deleted")
async def on_model_delete(event: EntityEvent, log: Logger) -> None:
    log.info(f"Model deleted: {event.model_name} with id {event.entity_id}")


@router.subscriber("auth.user-logged-in")
@router.publisher("user-login-postprocess")
async def on_user_logged_in(event: UserEvent, log: Logger) -> str:
    log.info(f"User Logged In: {event.id}")
    return event.id


@router.subscriber("user-login-postprocess")
async def postprocess_logged_in_user(user_id: str, log: Logger):
    log.debug(f'🚀 USER PROCESS {user_id}')
