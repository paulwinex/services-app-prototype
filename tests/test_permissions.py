import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.groups.permissions import GroupPermission
from app.modules.permissions.permissions import PermissionPermission
from app.modules.permissions.repository import PermissionRepository
from app.modules.permissions.schemas import PermissionCreateRequest
from app.modules.permissions.service import PermissionService
from app.modules.users.permissions import UserPermission
from app.core.startup.init_db import _init_permissions


async def create_test_permissions(async_db_session: AsyncSession):
    await _init_permissions(async_db_session)
    return
    service = PermissionService(repository=PermissionRepository(async_db_session))
    all_permissions = (
        list(UserPermission) + list(GroupPermission) + list(PermissionPermission)
    )

    for perm_enum in all_permissions:
        codename = str(perm_enum)
        existing = await service.get_by_codename(codename)
        if existing:
            continue

        perm_data = PermissionCreateRequest(
            name=perm_enum.name.replace("_", " ").title(),
            codename=codename,
        )
        await service.create(perm_data)


class TestPermissionList:
    @pytest.mark.asyncio
    async def test_list_permissions_success(
        self, admin_client: AsyncClient, async_db_session
    ):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get("/api/v1/permissions")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["items"], list)
        assert data["total"] >= 17

    @pytest.mark.asyncio
    async def test_list_permissions_with_pagination(
        self, admin_client: AsyncClient, async_db_session
    ):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get("/api/v1/permissions?limit=5&offset=0")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["limit"] == 5
        assert data["offset"] == 0

    @pytest.mark.asyncio
    async def test_list_permissions_filter_by_name(
        self, admin_client: AsyncClient, test_permission, async_db_session
    ):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get(
            f"/api/v1/permissions?name={test_permission.name}"
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data["items"]) >= 1
        assert data["items"][0]["name"] == test_permission.name

    @pytest.mark.asyncio
    async def test_list_permissions_filter_by_codename(
        self, admin_client: AsyncClient, test_permission, async_db_session
    ):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get(
            f"/api/v1/permissions?codename={test_permission.codename}"
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data["items"]) >= 1
        assert data["items"][0]["codename"] == test_permission.codename

    @pytest.mark.asyncio
    async def test_list_permissions_unauthorized(
        self, client: AsyncClient, async_db_session
    ):
        await create_test_permissions(async_db_session)
        resp = await client.get("/api/v1/permissions")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestPermissionGet:
    @pytest.mark.asyncio
    async def test_get_permission_by_id(
        self, admin_client: AsyncClient, test_permission, async_db_session
    ):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get(f"/api/v1/permissions/{test_permission.id}")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["id"] == str(test_permission.id)
        assert data["name"] == test_permission.name
        assert data["codename"] == test_permission.codename

    @pytest.mark.asyncio
    async def test_get_nonexistent_permission(
        self, admin_client: AsyncClient, async_db_session
    ):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get(
            "/api/v1/permissions/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_permission_by_codename(
        self, admin_client: AsyncClient, test_permission, async_db_session
    ):
        resp = await admin_client.get(
            f"/api/v1/permissions?codename={test_permission.codename}"
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["items"][0]["codename"] == test_permission.codename

    @pytest.mark.asyncio
    async def test_get_permission_by_nonexistent_codename(
        self, admin_client: AsyncClient, async_db_session
    ):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get(
            "/api/v1/permissions/codename/nonexistent.codename"
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_permission_unauthorized(
        self, client: AsyncClient, test_permission, async_db_session
    ):
        await create_test_permissions(async_db_session)
        resp = await client.get(f"/api/v1/permissions/{test_permission.id}")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestPermissionAutoDiscovery:
    """Tests for permission auto-discovery."""

    # Expected minimum permission count: UserPermission(5) + GroupPermission(7) + PermissionPermission(5) = 17
    MIN_EXPECTED_PERMISSION_COUNT = 17

    @pytest.mark.asyncio
    async def test_permissions_exist_in_database(
        self, admin_client: AsyncClient, async_db_session
    ):
        """Test that permissions were auto-discovered and created."""
        await create_test_permissions(async_db_session)
        resp = await admin_client.get("/api/v1/permissions")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["total"] >= self.MIN_EXPECTED_PERMISSION_COUNT

    @pytest.mark.asyncio
    async def test_user_permissions_exist(
        self, admin_client: AsyncClient, async_db_session
    ):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get("/api/v1/permissions?codename=user.can_list")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data["items"]) >= 1
        assert data["items"][0]["codename"] == "user.can_list"

    @pytest.mark.asyncio
    async def test_group_permissions_exist(
        self, admin_client: AsyncClient, async_db_session
    ):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get("/api/v1/permissions?codename=group.can_list")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data["items"]) >= 1
        assert data["items"][0]["codename"] == "group.can_list"

    @pytest.mark.asyncio
    async def test_permission_permissions_exist(
        self, admin_client: AsyncClient, async_db_session
    ):
        await create_test_permissions(async_db_session)
        resp = await admin_client.get(
            "/api/v1/permissions?codename=permission.can_list"
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data["items"]) >= 1
        assert data["items"][0]["codename"] == "permission.can_list"
