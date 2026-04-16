import pytest
from httpx import AsyncClient
from fastapi import status


class TestAuth:

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_settings):
        resp = await client.post(
            '/api/v1/auth/login', data={
                'username': test_settings.ADMIN_EMAIL,
                'password': test_settings.ADMIN_PASSWORD.get_secret_value(),
                'grant_type': 'password',
            },
            headers={'accept': 'application/json'}
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['access_token_expire'] > 0
        assert data['refresh_token_expire'] > 0

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient, test_settings):
        resp = await client.post(
            '/api/v1/auth/login', data={
                'username': test_settings.ADMIN_EMAIL,
                'password': 'wrongpassword123',
                'grant_type': 'password',
            },
            headers={'accept': 'application/json'}
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        resp = await client.post(
            '/api/v1/auth/login', data={
                'username': 'nonexistent@test.com',
                'password': 'somepassword123',
                'grant_type': 'password',
            },
            headers={'accept': 'application/json'}
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_current_user_profile(self, admin_client: AsyncClient):
        resp = await admin_client.get('/api/v1/auth/me')
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data.get('id') is not None
        assert data.get('email') == 'admin@test.com'
        assert data.get('first_name') == 'Super'
        assert data.get('last_name') == 'Admin'

    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        resp = await client.get('/api/v1/auth/me')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_refresh_token(self, client: AsyncClient, test_settings):
        login_resp = await client.post(
            '/api/v1/auth/login', data={
                'username': test_settings.ADMIN_EMAIL,
                'password': test_settings.ADMIN_PASSWORD.get_secret_value(),
                'grant_type': 'password',
            },
            headers={'accept': 'application/json'}
        )
        assert login_resp.status_code == status.HTTP_200_OK
        refresh_token = login_resp.json()['refresh_token']
        resp = await client.post(
            '/api/v1/auth/refresh',
            json={'refresh_token': refresh_token},
            headers={'accept': 'application/json'}
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert 'access_token' in data
        assert 'refresh_token' in data

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient):
        resp = await client.post(
            '/api/v1/auth/refresh',
            json={'refresh_token': 'invalid_token'},
            headers={'accept': 'application/json'}
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_refresh_token_empty(self, client: AsyncClient):
        resp = await client.post(
            '/api/v1/auth/refresh',
            json={'refresh_token': ''},
            headers={'accept': 'application/json'}
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
