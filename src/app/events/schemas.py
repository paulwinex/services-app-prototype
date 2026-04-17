from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.shared.utils import utcnow


class BaseEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=utcnow)


class ModelEvent(BaseEvent):
    model_name: str
    object_id: str|UUID
    event_type: str = None


class ModelCreateEvent(ModelEvent):
    event_type: str = "create"


class ModelUpdateEvent(ModelEvent):
    event_type: str = "update"


class ModelDeleteEvent(ModelEvent):
    event_type: str = "delete"


