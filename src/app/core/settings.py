from functools import cached_property, cache

from pydantic import Field, SecretStr, PostgresDsn, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_AUTH_")

    JWT_SECRET: SecretStr
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_SECONDS: int = 900
    JWT_REFRESH_EXPIRE_SECONDS: int = 604800


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_DB_")

    HOST: str = "localhost"
    PORT: int = 5432
    NAME: str = "db_name"
    USER: str = "db_user"
    PASSWORD: SecretStr = "no_password"

    @cached_property
    def dsn(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.USER,
                password=self.PASSWORD.get_secret_value(),
                host=self.HOST,
                port=self.PORT,
                path=self.NAME,
            )
        )


class EventsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_EVENTS_")

    URL: str = "nats://localhost:4222"
    ENABLE: bool = True


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    NAME: str = Field(default="NoName")
    DESCRIPTION: str = Field(default="No Description")
    DEBUG: bool = False
    DEFAULT_PORT: int = 8000
    DEFAULT_HOST: str = "0.0.0.0"

    AUTH: AuthSettings = Field(default_factory=AuthSettings)
    DB: DatabaseSettings = Field(default_factory=DatabaseSettings)
    EVENTS: EventsSettings = Field(default_factory=EventsSettings)

    ADMIN_EMAIL: EmailStr
    ADMIN_PASSWORD: SecretStr
    ADMIN_PHONE_NUMBER: str


@cache
def get_settings(**kwargs) -> Settings:
    return Settings(**kwargs)
