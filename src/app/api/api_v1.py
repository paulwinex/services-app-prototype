from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.groups.router import router as groups_router
from app.modules.permissions.router import router as permissions_router


v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
v1_router.include_router(users_router, prefix="/users", tags=["Users"])
v1_router.include_router(groups_router, prefix="/groups", tags=["Groups"])
v1_router.include_router(permissions_router, prefix="/permissions", tags=["Permissions"])
