from typing import Any

from loguru import logger
from sqlalchemy import inspect

from app.events.router import event
from app.events.schemas import ModelEvent


def _get_model_data(obj: Any) -> Any:
    mapper = inspect(obj.__class__)
    return mapper.local_table.name


@event('model.created')
async def on_model_create(obj: Any) -> ModelEvent:
    logger.debug(f'Model created event {obj}')
    return ModelEvent(model_name=_get_model_data(obj), object_id=obj.id, event_type="create")



@event('model.updated')
async def on_model_update(obj: Any) -> ModelEvent:
    logger.debug(f'Model update event {obj}')
    return ModelEvent(model_name=_get_model_data(obj), object_id=obj.id, event_type="update")


@event('model.deleted')
async def on_model_delete(obj: Any) -> ModelEvent:
    logger.debug(f'Model delete event {obj}')
    return ModelEvent(model_name=_get_model_data(obj), object_id=obj.id, event_type="delete")
