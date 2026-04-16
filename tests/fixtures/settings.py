import pytest

from app.core.settings import Settings, get_settings


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    # Clear the cached settings to ensure we get a fresh instance
    get_settings.cache_clear()

    # Create test settings with overridden values
    return get_settings(
        DB__HOST="test",
        DB__NAME="test",
        DB__USER="test",
        DB__PASSWORD="test",
        ADMIN_EMAIL="admin@test.com",
        ADMIN_PASSWORD="admin@test.com",
        ADMIN_PHONE_NUMBER="+78880000000",
        JWT_SECRET="test-secret-key-for-testing-purposes-only",
    )
