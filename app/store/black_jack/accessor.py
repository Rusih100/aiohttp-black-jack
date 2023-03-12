import typing
from typing import List

from sqlalchemy import delete, exc, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import ChunkedIteratorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.base.base_accessor import BaseAccessor
from app.black_jack.models import (
    Chat,
    ChatModel,
    Game,
    GameModel,
    Player,
    PlayerModel,
    State,
    StateModel,
    User,
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
                    join_players_count=0,
                    state=StateModel(type=GameStates.WAITING_NUMBER_OF_PLAYERS),
                )
                new_users = [
                    {
                        "vk_id": profile.id,
                        "first_name": profile.first_name,
                        "last_name": profile.last_name,
                        "is_admin": profile.is_admin,
                    }
                    for profile in profiles
                ]
                session.add(new_game)
                await session.execute(
                    insert(UserModel).values(new_users).on_conflict_do_nothing()
                )

        return await self.get_game_by_chat_id(chat_id=chat_id)

    async def close_game(self, chat_id: int):
        async with self.app.database.session() as session:
            session: AsyncSession
            async with session.begin():
                await session.execute(
                    delete(GameModel).where(GameModel.chat_id == chat_id)
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

    async def get_game_by_game_id(self, game_id: int) -> Game | None:
        async with self.app.database.session() as session:
            session: AsyncSession

            result: ChunkedIteratorResult = await session.execute(
                select(GameModel).where(GameModel.game_id == game_id)
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
            await session.commit()

        return await self.get_state_by_game_id(game_id=game_id)

    async def get_user_by_vk_id(self, vk_id: int) -> User | None:
        async with self.app.database.session() as session:
            session: AsyncSession

            result: ChunkedIteratorResult = await session.execute(
                select(UserModel).where(UserModel.vk_id == vk_id)
            )
            user = result.scalar()

        if user is None:
            return None

        return User.from_sqlalchemy(user)

    async def update_players_count(
        self, game_id: int, players_count: int
    ) -> None:
        async with self.app.database.session() as session:
            session: AsyncSession

            await session.execute(
                update(GameModel)
                .where(GameModel.game_id == game_id)
                .values(players_count=players_count)
            )
            await session.commit()

    async def create_player(
        self, game_id: int, vk_id: int, cash: int = 1000
    ) -> Player:
        async with self.app.database.session() as session:
            session: AsyncSession
            async with session.begin():
                user = await self.get_user_by_vk_id(vk_id=vk_id)
                game = await self.get_game_by_game_id(game_id=game_id)

                new_player = PlayerModel(
                    game_id=game_id, user_id=user.user_id, cash=cash
                )
                session.add(new_player)
                await session.execute(
                    update(GameModel)
                    .where(GameModel.game_id == game_id)
                    .values(join_players_count=game.join_players_count + 1)
                )

        return await self.get_player_by_game_id_and_vk_id(
            game_id=game_id, vk_id=vk_id
        )

    async def get_player_by_game_id_and_vk_id(
        self,
        game_id: int,
        vk_id: int,
    ) -> Player | None:
        async with self.app.database.session() as session:
            session: AsyncSession
            async with session.begin():
                user = await self.get_user_by_vk_id(vk_id=vk_id)
                if user is None:
                    return None

                result: ChunkedIteratorResult = await session.execute(
                    select(PlayerModel)
                    .where(PlayerModel.game_id == game_id)
                    .where(PlayerModel.user_id == user.user_id)
                )
                player = result.scalar()

        if player is None:
            return None

        return Player.from_sqlalchemy(player)
