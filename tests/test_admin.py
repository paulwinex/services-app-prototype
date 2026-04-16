import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.service import hash_password
from app.modules.users.models import UserModel
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreateRequest
from app.shared.exceptions import NotFoundError
from app.modules.users.service import UserService
import faker

f = faker.Faker()


class TestAdminUserOperations:
    @pytest.mark.asyncio
    async def test_admin_can_create_user(self, admin_client: AsyncClient):
        user_data = {
            "email": f.email(),
            "phone_number": f.phone_number(),
            "password": "password123",
            "first_name": f.first_name(),
            "last_name": f.last_name(),
        }
        resp = await admin_client.post("/api/v1/users", json=user_data)
        assert resp.status_code == status.HTTP_201_CREATED
        data = resp.json()
        assert data["email"] == user_data["email"]
        assert data["phone_number"] == user_data["phone_number"]

    @pytest.mark.asyncio
    async def test_admin_can_list_all_users(self, admin_client: AsyncClient):
        resp = await admin_client.get("/api/v1/users")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert "items" in data
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_admin_can_get_any_user(
        self, admin_client: AsyncClient, regular_user
    ):
        resp = await admin_client.get(f"/api/v1/users/{regular_user.id}")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["id"] == str(regular_user.id)

    @pytest.mark.asyncio
    async def test_admin_can_update_any_user(
        self, admin_client: AsyncClient, regular_user
    ):
        update_data = {
            "first_name": "Updated By Admin",
            "last_name": "Name",
        }
        resp = await admin_client.patch(
            f"/api/v1/users/{regular_user.id}", json=update_data
        )
        assert resp.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_admin_can_delete_non_admin_user(
        self, admin_client: AsyncClient, async_db_session: AsyncSession
    ):
        service = UserService(repository=UserRepository(async_db_session))
        user_data = dict(
            email="deletable2@test.com",
            phone_number=f.phone_number(),
            password="password123",
            first_name="Delete",
            last_name="Me",
            is_active=True,
            is_superuser=False,
            is_verified=False,
        )
        await service.create(user_data)
        created_user = await service.get_by_email("deletable2@test.com")
        user_id = str(created_user.id)

        resp = await admin_client.delete(f"/api/v1/users/{user_id}")
        assert resp.status_code == status.HTTP_204_NO_CONTENT

        with pytest.raises(NotFoundError):
            await service.get_by_id(user_id)

    @pytest.mark.asyncio
    async def test_admin_cannot_delete_admin_user(
        self, admin_client: AsyncClient, admin_user
    ):
        resp = await admin_client.delete(f"/api/v1/users/{admin_user.id}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_admin_can_change_any_user_password(
        self, admin_client: AsyncClient, regular_user, async_db_session, test_settings
    ):
        password_data = {
            "current_password": "regularpass123",
            "new_password": "newpassword456",
        }
        resp = await admin_client.post(
            f"/api/v1/users/{regular_user.id}/change-password", json=password_data
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT


class TestRegularUserRestrictions:
    @pytest.mark.asyncio
    async def test_regular_user_cannot_create_users(
        self, authenticated_client: AsyncClient
    ):
        user_data = {
            "email": f.email(),
            "phone_number": f.phone_number(),
            "password": "password123",
            "first_name": "No",
            "last_name": "User",
        }
        resp = await authenticated_client.post("/api/v1/users", json=user_data)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_regular_user_can_get_own_profile(
        self, authenticated_client: AsyncClient, regular_user
    ):
        resp = await authenticated_client.get("/api/v1/auth/me")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["email"] == str(regular_user.email)

    @pytest.mark.asyncio
    async def test_regular_user_cannot_delete_users(
        self, authenticated_client: AsyncClient, async_db_session
    ):
        user_to_delete = UserModel(
            email=f.email(),
            phone_number=f.phone_number(),
            password_hash=hash_password("password123"),
            first_name="To",
            last_name="Delete",
            is_active=True,
            is_superuser=False,
            is_verified=False,
        )
        async_db_session.add(user_to_delete)
        await async_db_session.commit()
        await async_db_session.refresh(user_to_delete)
        user_id = str(user_to_delete.id)

        resp = await authenticated_client.delete(f"/api/v1/users/{user_id}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN


class TestInactiveUserRestrictions:
    @pytest.mark.asyncio
    async def test_inactive_user_cannot_login(
        self, client: AsyncClient, async_db_session
    ):
        user_model = UserModel(
            email=f.email(),
            phone_number=f.phone_number(),
            password_hash=hash_password("inactivepass123"),
            first_name="Inactive",
            last_name="User",
            is_active=False,
            is_superuser=False,
            is_verified=False,
        )
        async_db_session.add(user_model)
        await async_db_session.commit()

        resp = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "inactive@test.com",
                "password": "inactivepass123",
                "grant_type": "password",
            },
            headers={"accept": "application/json"},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestAdminProfile:
    @pytest.mark.asyncio
    async def test_admin_profile_email(self, admin_client: AsyncClient):
        resp = await admin_client.get("/api/v1/auth/me")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data.get("email") == "admin@test.com"
        assert data.get("first_name") == "Super"
        assert data.get("last_name") == "Admin"
