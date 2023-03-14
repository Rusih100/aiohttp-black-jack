from aiohttp.web_exceptions import HTTPNotFound
from aiohttp_apispec import docs, querystring_schema

from app.black_jack.schemes import (
    GameGetQuerySchema,
    GameGetResponseSchema,
    GameSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.schemes import ErrorResponseSchema
from app.web.utils import json_response


# TODO: авториазция
class GetGameView(View):
    @docs(
        tags=["Game"],
        summary="Get game",
        description="Returns all information about the game by chat_id vk",
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
