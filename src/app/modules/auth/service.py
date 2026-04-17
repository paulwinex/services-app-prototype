import logging
from datetime import timedelta

import bcrypt
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError

from app.core.settings import get_settings
from app.modules.auth.events import on_user_logged_in
from app.modules.auth.schemas import TokenResponse
from app.modules.users.exceptions import InvalidCredentialsError
from app.modules.users.schemas import UserSchema
from app.modules.users.service import UserService
from app.shared.utils import utcnow


def create_auth_token(user_id: str) -> TokenResponse:
    settings = get_settings()
    now = utcnow()

    access_expire = now + timedelta(seconds=settings.AUTH.JWT_ACCESS_EXPIRE_SECONDS)
    access_payload = {
        "alg": settings.AUTH.JWT_ALGORITHM,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(access_expire.timestamp()),
        "sub": str(user_id),
        "type": "access",
    }
    access_token = jwt.encode(
        access_payload,
        settings.AUTH.JWT_SECRET.get_secret_value(),
        algorithm=settings.AUTH.JWT_ALGORITHM,
    )

    refresh_expire = now + timedelta(seconds=settings.AUTH.JWT_REFRESH_EXPIRE_SECONDS)
    refresh_payload = {
        "alg": settings.AUTH.JWT_ALGORITHM,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(refresh_expire.timestamp()),
        "sub": str(user_id),
        "type": "refresh",
    }
    refresh_token = jwt.encode(
        refresh_payload,
        settings.AUTH.JWT_SECRET.get_secret_value(),
        algorithm=settings.AUTH.JWT_ALGORITHM,
    )

    return TokenResponse(
        access_token=access_token,
        access_token_expire=int(access_expire.timestamp()),
        refresh_token=refresh_token,
        refresh_token_expire=int(refresh_expire.timestamp()),
    )


def decode_token(token: str, verify_exp: bool = True) -> dict:
    settings = get_settings()
    return jwt.decode(
        token,
        settings.AUTH.JWT_SECRET.get_secret_value(),
        algorithms=[settings.AUTH.JWT_ALGORITHM],
        options={"verify_exp": verify_exp},
    )


def validate_token(token: str) -> str:
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise InvalidCredentialsError("Invalid token type")
    except ExpiredSignatureError:
        raise InvalidCredentialsError("Token has expired")
    except JWTError as e:
        logging.exception(f"JWT decode error: {e}")
        raise InvalidCredentialsError("Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidCredentialsError("Invalid token payload")
    return user_id


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.user_service.authenticate(email, password)
        await on_user_logged_in(user)
        await self.user_service.repository.update(user.id, dict(last_login_at=utcnow()))
        return create_auth_token(user.id)

    async def get_user_by_token(self, token: str) -> UserSchema:
        user_id = validate_token(token)
        return UserSchema.model_validate(await self.user_service.get_by_id(user_id))

    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise InvalidCredentialsError("Invalid refresh token type")
        except JWTError as e:
            logging.exception(f"JWT decode error: {e}")
            raise InvalidCredentialsError("Invalid refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidCredentialsError("Invalid refresh token payload")
        return create_auth_token(user_id)


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
