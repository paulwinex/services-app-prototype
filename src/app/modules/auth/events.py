from loguru import logger

from app.core.events.event_decorator import event
from app.modules.users.schemas import UserSchema, UserEvent


@event("auth.user-logged-in")
async def on_user_logged_in(user: UserSchema) -> UserEvent:
    logger.debug(f'User logged in event {user.id}')
    return UserEvent(id=user.id)

