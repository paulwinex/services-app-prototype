from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator, AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker, create_async_engine

from app.core.settings import get_settings


class DatabaseSession:
    def __init__(self, dsn: str = None):
        self._settings = get_settings()
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._dsn = dsn or self._settings.DB.dsn

    def setup(self) -> None:
        self._engine = create_async_engine(
            self._dsn,
            echo=self._settings.DEBUG,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    async def shutdown(self) -> None:
        if self._engine:
            await self._engine.dispose()

    @asynccontextmanager
    async def get_session(self) -> AsyncIterator[AsyncSession]:
        if not self._session_factory:
            raise RuntimeError("Database session not initialized. Call setup() first.")
        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @property
    def engine(self) -> AsyncEngine:
        if not self._engine:
            raise RuntimeError("Database engine not initialized. Call setup() first.")
        return self._engine


async_session = DatabaseSession()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session.get_session() as session:
        yield session



SessionDEP = Annotated[AsyncSession, Depends(get_async_session)]
