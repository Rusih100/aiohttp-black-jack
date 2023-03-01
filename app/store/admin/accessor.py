import typing

from sqlalchemy import select
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.models import Admin, AdminModel
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        self.app = app

        await self._create_admin_at_startup()

    async def _create_admin_at_startup(self):
        config = self.app.config.admin

        email = config.email
        password = config.password

        if not await self.get_by_email(email):
            await self.create_admin(email=email, password=password)

    async def get_by_email(self, email: str) -> Admin | None:
        async with self.app.database.session() as session:
            session: AsyncSession

            result: ChunkedIteratorResult = await session.execute(
                select(AdminModel).where(AdminModel.email == email)
            )
            admin = result.scalar()

        return Admin.from_sqlalchemy(admin) if admin else None

    async def create_admin(self, email: str, password: str) -> Admin:
        async with self.app.database.session() as session:
            session: AsyncSession

            new_admin = AdminModel(
                email=email, password=Admin.password_to_hash(password)
            )

            session.add(new_admin)
            await session.commit()

        return Admin.from_sqlalchemy(new_admin)
