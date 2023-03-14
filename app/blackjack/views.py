from aiohttp.web_exceptions import HTTPNotFound
from aiohttp_apispec import docs, querystring_schema

from app.blackjack.schemes import (
    GameGetQuerySchema,
    GameGetResponseSchema,
    GameSchema,
    GameListResponseSchema,
    UserListResponseSchema,
    UserSchema
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.schemes import ErrorResponseSchema
from app.web.utils import json_response


class GameInfoView(AuthRequiredMixin, View):
    @docs(
        tags=["Game"],
        summary="Get game information by chat_id",
        description="Gets information about the current game by chat_id vk",
        responses={
            200: {  # Успешно
                "description": "Ok",
                "schema": GameGetResponseSchema,
            },
            400: {  # Непреобразуемая сущность
                "description": "Error: Bad request",
                "schema": ErrorResponseSchema,
            },
            401: {  # Неавторизован
                "description": "Error: Unauthorized",
                "schema": ErrorResponseSchema,
            },
            404: {  # Не существует
                "description": "Error: Not found",
                "schema": ErrorResponseSchema,
            },
            405: {  # Не реализовано
                "description": "Error: Not implemented",
                "schema": ErrorResponseSchema,
            },
        },
    )
    @querystring_schema(GameGetQuerySchema)
    async def get(self):
        chat_id = self.request.query.get("chat_id")
        chat_id = int(chat_id) if chat_id else None

        raw_game = await self.store.game.get_game_by_chat_id(chat_id=chat_id)

        if raw_game is None:
            raise HTTPNotFound(reason="Game not found")

        return json_response(data=GameSchema().dump(raw_game))


class GameListView(AuthRequiredMixin, View):
    @docs(
        tags=["Game"],
        summary="Gets a list of running games",
        description="Gets a list of running games",
        responses={
            200: {  # Успешно
                "description": "Ok",
                "schema": GameListResponseSchema,
            },
            401: {  # Неавторизован
                "description": "Error: Unauthorized",
                "schema": ErrorResponseSchema,
            },
            405: {  # Не реализовано
                "description": "Error: Not implemented",
                "schema": ErrorResponseSchema,
            },
        },
    )
    async def get(self):
        raw_games = await self.store.game.get_all_games()

        games = [GameSchema(only=("game_id", "chat_id")).dump(raw_game) for raw_game in raw_games]

        return json_response(data={"games": games})


class UserListView(AuthRequiredMixin, View):
    @docs(
        tags=["User"],
        summary="Gets a list of all users",
        description="Gets a list of all users",
        responses={
            200: {  # Успешно
                "description": "Ok",
                "schema": UserListResponseSchema,
            },
            401: {  # Неавторизован
                "description": "Error: Unauthorized",
                "schema": ErrorResponseSchema,
            },
            405: {  # Не реализовано
                "description": "Error: Not implemented",
                "schema": ErrorResponseSchema,
            },
        },
    )
    async def get(self):
        raw_users = await self.store.game.get_all_users()

        users = [
            UserSchema(only=("user_id", "vk_id", "first_name", "last_name"))
            .dump(raw_user) for raw_user in raw_users
        ]

        return json_response(data={"users": users})


