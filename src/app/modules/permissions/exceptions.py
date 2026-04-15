from app.shared.exceptions import NotFoundError, ConflictError


class PermissionNotFoundError(NotFoundError):
    pass


class PermissionAlreadyExistsError(ConflictError):
    pass
