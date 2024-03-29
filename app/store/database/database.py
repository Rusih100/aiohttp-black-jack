import asyncio
from logging import getLogger
from typing import TYPE_CHECKING, Optional

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from app.store.database.sqlalchemy_base import db

if TYPE_CHECKING:
    from app.web.app import Application


class Database:
    def __init__(self, app: "Application"):
        self.app = app
        self.logger = getLogger("database")
        self._engine: Optional[AsyncEngine] = None
        self._db: Optional[declarative_base] = None
        self.session: Optional[sessionmaker] = None

    async def _ping(self):
        async with self.session() as session:
            session: AsyncSession
            await session.execute("SELECT 1;")

    async def connect(self, *_: list, **__: dict) -> None:
        self._db = db

        config = self.app.config.database

        connection_url = URL.create(
            drivername="postgresql+asyncpg",
            username=config.user,
            password=config.password,
            host=config.host,
            port=config.port,
            database=config.database,
        )

        self._engine = create_async_engine(
            connection_url, echo=False, future=True
        )

        self.session = sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )
        try:
            await self._ping()
        except ConnectionRefusedError:
            self.logger.error(
                "Database connection error. We will try again in 5 seconds"
            )
            await asyncio.sleep(5)
            await self.connect(*_, **__)

    async def disconnect(self, *_: list, **__: dict) -> None:
        if self.session is not None:
            self.session.close_all()
            self.session = None

        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None

        if self._db is not None:
            self._db = None
