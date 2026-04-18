from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.shared.utils import utcnow


class BaseEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=utcnow)


class EntityEvent(BaseEvent):
    model_name: str
    entity_id: str | UUID
    event_type: str = None


class EntityCreateEvent(EntityEvent):
    event_type: str = "create"


class EntityUpdateEvent(EntityEvent):
    event_type: str = "update"


class EntityDeleteEvent(EntityEvent):
    event_type: str = "delete"


