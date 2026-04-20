from app.core.events import get_event_router
from app.modules.users.schemas import UserEvent

roter = get_event_router()

@roter.subscriber('auth.user-logged-in')
async def on_user_logged_in(user: UserEvent):
    """Callbacks example"""
    print('USER LOGGED IN', user)