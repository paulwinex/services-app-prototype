import logging

from .routes import router as dev_router
from ...core.settings import get_settings


def init_dev(app):
    settings = get_settings()
    if settings.STATE.DEBUG:
        logging.warning('⚠️ INIT DEV ROUTES')
        app.include_router(dev_router, prefix="/dev")