import typing

from sqlalchemy import exc, select
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.base.base_accessor import BaseAccessor
from app.black_jack.models import Chat, ChatModel, Game, GameModel

if typing.TYPE_CHECKING:
    from app.web.app import Application


class GameAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        self.app = app

    async def create_chat(self, chat_id: int) -> Chat:
        async with self.app.database.session() as session:
            session: AsyncSession

            new_chat = ChatModel(chat_id=chat_id)

            try:
                session.add(new_chat)
                await session.commit()

            except exc.IntegrityError:
                await session.rollback()
                return await self.get_chat_by_id(chat_id=chat_id)

        return Chat.from_sqlalchemy(new_chat)

    async def get_chat_by_id(self, chat_id: int) -> Chat | None:
        async with self.app.database.session() as session:
            session: AsyncSession

            result: ChunkedIteratorResult = await session.execute(
                select(ChatModel).where(ChatModel.chat_id == chat_id)
            )
            chat = result.scalar()

        if chat is None:
            return None

        return Chat.from_sqlalchemy(chat)

    async def create_game(self, chat_id: int) -> Game:
        async with self.app.database.session() as session:
            session: AsyncSession

            new_game = GameModel(
                chat_id=chat_id,
                players_count=0,
            )

            try:
                session.add(new_game)
                await session.commit()

            except exc.IntegrityError:
                await session.rollback()
                return await self.get_game_by_chat_id(chat_id=chat_id)

        return Game.from_sqlalchemy(new_game)

    async def get_game_by_chat_id(self, chat_id: int) -> Game | None:
        async with self.app.database.session() as session:
            session: AsyncSession

            result: ChunkedIteratorResult = await session.execute(
                select(GameModel).where(GameModel.chat_id == chat_id)
                .options(
                    joinedload("players"), joinedload("chat"), joinedload("state")
                )
            )
            game = result.scalar()

        if game is None:
            return None

        return Game.from_sqlalchemy(game)
