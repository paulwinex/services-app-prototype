from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1 import v1_router
from app.core.exception_handlers import setup_exception_handlers
from app.core.settings import get_settings
from app.core.startup import lifespan


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version='0.0.1',
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    # TODO add from settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_exception_handlers(app)
    app.include_router(v1_router)

    @app.get("/", include_in_schema=False)
    async def index(request: Request):
        from app import __version__
        base_url = str(request.base_url).rstrip("/")
        app_info_dict = {
            "app_name": "SequoiaAi",
            "description": "SequoiaAi App Backend",
            "version": __version__,
            "swagger": f"{base_url}/docs",
            "redoc": f"{base_url}/redoc"
        }
        return app_info_dict

    @app.get("/health", include_in_schema=False)
    async def health_check():
        return {"status": "healthy", "app": settings.NAME}

    return app
