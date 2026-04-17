from typing import TypeVar
from pydantic import BaseModel
from app.shared.base_model import BaseDBModel


TModel = TypeVar("TModel", bound=BaseDBModel)
TSchema = TypeVar("TSchema", bound=BaseModel)