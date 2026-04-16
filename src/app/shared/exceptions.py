from typing import Any
from http import HTTPStatus


class AppError(Exception):
    """Base application error"""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(
        self,
        detail: str | None = None,
        status: int | HTTPStatus = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ):
        self.detail = detail or self.__doc__ or "An error occurred"
        self.status = status or self.status_code
        self.headers = headers
        self.extra = kwargs
        super().__init__(self.detail)

    @property
    def code(self):
        return self.status.value if isinstance(self.status, HTTPStatus) else self.status

    @property
    def message(self):
        return self.detail or self.status.phrase


class NotFoundError(AppError):
    """Entity not found"""

    status_code = HTTPStatus.NOT_FOUND


class ConflictError(AppError):
    """Conflict error"""

    status_code = HTTPStatus.CONFLICT


class UnauthorizedError(AppError):
    """Unauthorized"""

    status_code = HTTPStatus.UNAUTHORIZED


class ForbiddenError(AppError):
    """Forbidden"""

    status_code = HTTPStatus.FORBIDDEN


class NoPermissionError(AppError):
    """No Permission"""

    status_code = HTTPStatus.FORBIDDEN


class ValidationError(AppError):
    """Validation error"""

    status_code = HTTPStatus.BAD_REQUEST


class RequestValueError(AppError):
    """Request value error"""

    status_code = HTTPStatus.BAD_REQUEST