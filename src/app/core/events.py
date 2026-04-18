from typing import Any

from loguru import logger
from sqlalchemy import inspect

from app.events.router import event
from app.events.schemas import EntityEvent


def _get_model_data(obj: Any) -> Any:
    mapper = inspect(obj.__class__)
    return mapper.local_table.name


@event('entity.created')
async def on_model_create(obj: Any) -> EntityEvent:
    logger.debug(f'Entity created event {obj}')
    return EntityEvent(model_name=_get_model_data(obj), entity_id=obj.id, event_type="create")



@event('entity.updated')
async def on_model_update(obj: Any) -> EntityEvent:
    logger.debug(f'Entity update event {obj}')
    return EntityEvent(model_name=_get_model_data(obj), entity_id=obj.id, event_type="update")


@event('entity.deleted')
async def on_model_delete(obj: Any) -> EntityEvent:
    logger.debug(f'Entity delete event {obj}')
    return EntityEvent(model_name=_get_model_data(obj), entity_id=obj.id, event_type="delete")
