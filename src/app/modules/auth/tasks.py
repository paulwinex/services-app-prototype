from uuid import UUID

from loguru import logger

from app.core.tasks_broker import get_task_broker


broker = get_task_broker()


@broker.task
async def send_register_email(user_id: str|UUID):
    logger.debug(f'Send welcome email if user has it: [{user_id}]')
