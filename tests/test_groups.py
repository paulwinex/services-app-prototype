import uuid

import pytest
from httpx import AsyncClient
from fastapi import status

from app.modules.groups.models import GroupModel


class TestGroupCreate:
    @pytest.mark.asyncio
    async def test_create_group_success(self, admin_client: AsyncClient):
        unique_id = str(uuid.uuid7())[:8]
        group_data = {
            "name": f"New Test Group {unique_id}",
            "description": "Test group description",
        }
        resp = await admin_client.post("/api/v1/groups", json=group_data)
        assert resp.status_code == status.HTTP_201_CREATED
        data = resp.json()
        assert data["name"] == f"New Test Group {unique_id}"
        assert data["description"] == "Test group description"
        assert data["is_system"] is False
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_group_duplicate_name(
        self, admin_client: AsyncClient, test_group
    ):
        group_data = {
            "name": test_group.name,
            "description": "Duplicate group",
        }
        resp = await admin_client.post("/api/v1/groups", json=group_data)
        assert resp.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.asyncio
    async def test_create_group_empty_name(self, admin_client: AsyncClient):
        group_data = {
            "name": "",
            "description": "Empty name group",
        }
        resp = await admin_client.post("/api/v1/groups", json=group_data)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_create_group_long_name(self, admin_client: AsyncClient):
        group_data = {
            "name": "A" * 50,
            "description": "Long name group",
        }
        resp = await admin_client.post("/api/v1/groups", json=group_data)
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_create_group_unauthorized(self, client: AsyncClient):
        group_data = {
            "name": "Unauthorized Group",
            "description": "Should fail",
        }
        resp = await client.post("/api/v1/groups", json=group_data)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestGroupGet:
    @pytest.mark.asyncio
    async def test_get_group_by_id(self, admin_client: AsyncClient, test_group):
        resp = await admin_client.get(f"/api/v1/groups/{test_group.id}")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["id"] == str(test_group.id)
        assert data["name"] == test_group.name

    @pytest.mark.asyncio
    async def test_get_nonexistent_group(self, admin_client: AsyncClient):
        resp = await admin_client.get(
            "/api/v1/groups/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_group_unauthorized(self, client: AsyncClient, test_group):
        resp = await client.get(f"/api/v1/groups/{test_group.id}")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestGroupList:
    @pytest.mark.asyncio
    async def test_list_groups_success(self, admin_client: AsyncClient, test_group):
        resp = await admin_client.get("/api/v1/groups")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["items"], list)
        assert data["total"] >= 1
        assert any(g["id"] == str(test_group.id) for g in data["items"])

    @pytest.mark.asyncio
    async def test_list_groups_with_pagination(self, admin_client: AsyncClient):
        resp = await admin_client.get("/api/v1/groups?limit=1&offset=0")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert isinstance(data["items"], list)
        assert len(data["items"]) <= 1
        assert data["limit"] == 1
        assert data["offset"] == 0

    @pytest.mark.asyncio
    async def test_list_groups_filter_by_name(
        self, admin_client: AsyncClient, test_group
    ):
        resp = await admin_client.get(f"/api/v1/groups?name={test_group.name}")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == test_group.name

    @pytest.mark.asyncio
    async def test_list_groups_filter_by_is_system(
        self, admin_client: AsyncClient, system_group
    ):
        resp = await admin_client.get("/api/v1/groups?is_system=true")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert len(data["items"]) >= 1
        assert data["items"][0]["is_system"] is True

    @pytest.mark.asyncio
    async def test_list_groups_unauthorized(self, client: AsyncClient):
        resp = await client.get("/api/v1/groups")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestGroupUpdate:
    @pytest.mark.asyncio
    async def test_update_group_success(self, admin_client: AsyncClient, test_group):
        update_data = {
            "name": "Updated Group Name",
            "description": "Updated description",
        }
        resp = await admin_client.patch(
            f"/api/v1/groups/{test_group.id}", json=update_data
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        print(data)
        assert data["name"] == "Updated Group Name"
        assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_update_group_empty_body(self, admin_client: AsyncClient, test_group):
        resp = await admin_client.patch(f"/api/v1/groups/{test_group.id}", json={})
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["name"] == test_group.name
        assert data["description"] == test_group.description

    @pytest.mark.asyncio
    async def test_update_nonexistent_group(self, admin_client: AsyncClient):
        update_data = {"name": "Updated"}
        resp = await admin_client.patch(
            "/api/v1/groups/00000000-0000-0000-0000-000000000000", json=update_data
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_group_unauthorized(self, client: AsyncClient, test_group):
        update_data = {"name": "Updated"}
        resp = await client.patch(f"/api/v1/groups/{test_group.id}", json=update_data)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestGroupDelete:
    @pytest.mark.asyncio
    async def test_delete_group_success(
        self, admin_client: AsyncClient, async_db_session
    ):
        # Create group to delete
        group_model = GroupModel(
            id="00000000-0000-0000-0000-000000000001",
            name="To Delete",
            description="Will be deleted",
            is_system=False,
        )
        async_db_session.add(group_model)
        await async_db_session.commit()

        resp = await admin_client.delete(
            "/api/v1/groups/00000000-0000-0000-0000-000000000001"
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_delete_system_group_forbidden(
        self, admin_client: AsyncClient, system_group
    ):
        resp = await admin_client.delete(f"/api/v1/groups/{system_group.id}")
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_delete_nonexistent_group(self, admin_client: AsyncClient):
        resp = await admin_client.delete(
            "/api/v1/groups/00000000-0000-0000-0000-000000000000"
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_group_unauthorized(self, client: AsyncClient, test_group):
        resp = await client.delete(f"/api/v1/groups/{test_group.id}")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestGroupUserManagement:
    @pytest.mark.asyncio
    async def test_add_user_to_group(
        self, admin_client: AsyncClient, regular_user, test_group
    ):
        resp = await admin_client.post(
            f"/api/v1/groups/{test_group.id}/users/{regular_user.id}"
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_add_user_already_in_group(
        self, admin_client: AsyncClient, user_in_group, test_group
    ):
        resp = await admin_client.post(
            f"/api/v1/groups/{test_group.id}/users/{user_in_group.id}"
        )
        assert resp.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.asyncio
    async def test_remove_user_from_group(
        self, admin_client: AsyncClient, user_in_group, test_group
    ):
        resp = await admin_client.delete(
            f"/api/v1/groups/{test_group.id}/users/{user_in_group.id}"
        )
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_remove_user_not_in_group(
        self, admin_client: AsyncClient, regular_user, test_group
    ):
        resp = await admin_client.delete(
            f"/api/v1/groups/{test_group.id}/users/{regular_user.id}"
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND


class TestUserGroups:
    @pytest.mark.asyncio
    async def test_list_user_groups(
        self, admin_client: AsyncClient, user_in_group, test_group
    ):
        resp = await admin_client.get(f"/api/v1/groups/users/{user_in_group.id}/groups")
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert "items" in data
        assert len(data["items"]) >= 1
