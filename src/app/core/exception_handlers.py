from http import HTTPStatus

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.exc import DBAPIError

from app.shared.exceptions import AppError


def setup_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.error(f"AppError: {exc.message} | request={request.url}")
        return JSONResponse(
            status_code=exc.code,
            content={"detail": exc.message, "type": exc.__class__.__name__},
            headers=exc.headers,
        )

    @app.exception_handler(DBAPIError)
    async def db_error_handler(request: Request, exc: DBAPIError):
        message = f"Error: {exc.orig}. {exc.detail}"
        logger.exception(message)
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content={"detail": message, "type": exc.__class__.__name__},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(f"Unhandled exception: {exc} | request={request.url}")
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "type": exc.__class__.__name__},
        )
