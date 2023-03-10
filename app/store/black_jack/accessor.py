import typing
from typing import List

from sqlalchemy import exc, select, update, delete
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.base.base_accessor import BaseAccessor
from app.black_jack.models import (
    Chat,
    ChatModel,
    Game,
    GameModel,
    State,
    StateModel,
    UserModel,
)
from app.store.bot.states import GameStates
from app.store.vk_api.dataclasses import Profile

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

    async def init_game(
        self, chat_id: int, profiles: List[Profile]
    ) -> Game | None:
        async with self.app.database.session() as session:
            session: AsyncSession
            async with session.begin():
                new_game = GameModel(
                    chat_id=chat_id,
                    players_count=0,
                    state=StateModel(type=GameStates.WAITING_NUMBER_OF_PLAYERS),
                )
                new_users = [
                    UserModel(
                        vk_id=profile.id,
                        first_name=profile.first_name,
                        last_name=profile.last_name,
                        is_admin=profile.is_admin,
                    )
                    for profile in profiles
                ]
                session.add(new_game)
                session.add_all(new_users)

        return await self.get_game_by_chat_id(chat_id=chat_id)

    async def close_game(self, chat_id: int):
        async with self.app.database.session() as session:
            session: AsyncSession
            async with session.begin():
                await session.execute(
                    delete(GameModel)
                    .where(GameModel.chat_id == chat_id)
                )

    async def get_game_by_chat_id(self, chat_id: int) -> Game | None:
        async with self.app.database.session() as session:
            session: AsyncSession

            result: ChunkedIteratorResult = await session.execute(
                select(GameModel).where(GameModel.chat_id == chat_id)
            )
            game = result.scalar()

        if game is None:
            return None

        return Game.from_sqlalchemy(game)

    async def get_state_by_game_id(self, game_id: int) -> State | None:
        async with self.app.database.session() as session:
            session: AsyncSession

            result: ChunkedIteratorResult = await session.execute(
                select(StateModel)
                .where(StateModel.game_id == game_id)
                .options(joinedload("current_player"), joinedload("game"))
            )
            state = result.scalar()

        if state is None:
            return None

        return State.from_sqlalchemy(state)

    async def update_state_type(
        self, game_id: int, state_type: GameStates
    ) -> State:
        async with self.app.database.session() as session:
            session: AsyncSession

            await session.execute(
                update(StateModel)
                .where(StateModel.game_id == game_id)
                .values(type=state_type)
            )
            await session.commit()  # TODO: Отловить исключение

        return await self.get_state_by_game_id(game_id=game_id)
