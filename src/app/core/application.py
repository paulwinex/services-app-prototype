from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1 import v1_router
from app.core.exception_handlers import setup_exception_handlers
from app.core.settings import get_settings
from app.core.startup import lifespan
from app.events.router import get_event_router
import fastapi_swagger_dark as fsd


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.NAME,
        version="0.0.1",
        lifespan=lifespan,
        docs_url=None,
    )
    # apply middleware  > TODO add from settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # add exception handlers
    setup_exception_handlers(app)

    # apply dark theme
    dark_docs_router = APIRouter()
    fsd.install(dark_docs_router, path="/docs")
    app.include_router(dark_docs_router)

    # add main router
    app.include_router(v1_router)

    # add event router
    if settings.EVENTS.ENABLE:
        event_router = get_event_router()
        app.include_router(event_router)

    # root routes
    @app.get("/", include_in_schema=False)
    async def index(request: Request):
        from app import __version__

        base_url = str(request.base_url).rstrip("/")
        app_info_dict = {
            "app_name": settings.NAME,
            "description": settings.DESCRIPTION,
            "version": __version__,
            "swagger": f"{base_url}/docs",
            "redoc": f"{base_url}/redoc",
        }
        return app_info_dict

    @app.get("/health", include_in_schema=False)
    async def health_check():
        return {"status": "healthy", "app": settings.NAME}

    return app
