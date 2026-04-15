from app.shared.exceptions import NotFoundError, ConflictError, ForbiddenError


class GroupAlreadyExistsError(ConflictError):
    pass


class SuperUserGroupError(ForbiddenError):
    pass


class UserAlreadyInGroupError(ConflictError):
    pass


class UserNotInGroupError(NotFoundError):
    pass
