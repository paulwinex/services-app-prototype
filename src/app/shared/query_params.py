from typing import Optional

from fastapi import Query
from pydantic import BaseModel


class PaginationParams(BaseModel):
    limit: int = Query(50, ge=1, le=1000)
    offset: int = Query(0, ge=0)
    order_by: Optional[str] = Query("id")
    sorting: Optional[str] = Query("asc")
