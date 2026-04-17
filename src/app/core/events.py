from typing import Any

from loguru import logger
from sqlalchemy import inspect

from app.events.router import get_event_router
from app.events.schemas import ModelEvent
from app.shared.utils import events_enabled


async def _emit_model_event(obj: Any, event_type: str) -> None:
    router = get_event_router()
    if hasattr(obj, "id"):
        obj_id = str(obj.id)
    else:
        return
    mapper = inspect(obj.__class__)
    model_name = mapper.local_table.name

    event = ModelEvent(model_name=model_name, object_id=obj_id, event_type=event_type)
    await router.broker.publish(event.model_dump(mode='json'), subject=f"model.{model_name}.{event_type}")


@events_enabled
async def on_model_create(obj: Any) -> None:
    logger.debug(f'Model created event {obj}')
    await _emit_model_event(obj, "create")


@events_enabled
async def on_model_update(obj: Any) -> None:
    logger.debug(f'Model update event {obj}')
    await _emit_model_event(obj, "update")


@events_enabled
async def on_model_delete(obj: Any) -> None:
    logger.debug(f'Model delete event {obj}')
    await _emit_model_event(obj, "delete")


