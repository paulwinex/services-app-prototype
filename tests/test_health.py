import pytest
from fastapi import status
from httpx import AsyncClient


class TestHealth:

    @pytest.mark.asyncio
    async def test_app_health(self, client: AsyncClient):
        resp = await client.get('/health')
        assert resp.status_code == status.HTTP_200_OK
