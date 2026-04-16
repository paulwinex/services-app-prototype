from fastapi import APIRouter

from app.modules.auth.dependencies import AuthServiceDEP, ActiveUserDEP, LoginDataDEP
from app.modules.auth.schemas import TokenResponse, RefreshTokenRequest
from app.modules.users.schemas import UserResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: LoginDataDEP,
    service: AuthServiceDEP,
) -> TokenResponse:
    return await service.login(form_data.username, form_data.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    service: AuthServiceDEP,
) -> TokenResponse:
    return service.refresh_access_token(request.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    user: ActiveUserDEP,
):
    return user
