from app.shared.exceptions import ForbiddenError, UnauthorizedError


class InvalidCredentialsError(UnauthorizedError):
    pass


class UserInactiveError(ForbiddenError):
    pass
