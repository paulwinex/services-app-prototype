from loguru import logger

from app.core.settings import settings
from .routes import router as dev_router


def init_dev(app):
    if settings.STATE.DEBUG:
        logger.warning('⚠️ INIT DEV ROUTES')
        app.include_router(dev_router, prefix="/dev")