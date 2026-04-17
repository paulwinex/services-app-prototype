from loguru import logger

from app.shared.utils import events_enabled
from app.events.router import get_event_router
from app.modules.users.schemas import UserSchema, UserEvent


@events_enabled
async def on_user_logged_in(user: UserSchema) -> None:
    logger.debug(f'User logged in event {user.id}')
    router = get_event_router()
    event = UserEvent(id=user.id)
    await router.broker.publish(event.model_dump(mode='json'), subject="auth.user-logged-in")
