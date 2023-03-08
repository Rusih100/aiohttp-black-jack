import typing

from sqlalchemy import select
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.base_accessor import BaseAccessor
from app.black_jack.models import Chat, ChatModel

if typing.TYPE_CHECKING:
    from app.web.app import Application


class GameAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        self.app = app

    async def create_chat(self, chat_id) -> "Chat":
        async with self.app.database.session() as session:
            session: AsyncSession

            new_chat = ChatModel(chat_id=chat_id)

            session.add(new_chat)
            await session.commit()

        return Chat.from_sqlalchemy(new_chat)
