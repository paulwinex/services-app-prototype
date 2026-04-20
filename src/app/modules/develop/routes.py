from fastapi import APIRouter

from app.core.settings import settings
from .tasks import debug_task

router = APIRouter()


@router.get("/debug-task/{value}")
async def send_debug_task(value: int):
    task = await debug_task.kiq(value)
    result = await task.wait_result()
    return {'result': result}


@router.get("/settings")
async def get_settings():
    return settings.model_dump()


