import typing

from app.store.bot.router import Router
from app.store.vk_api.dataclasses import Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


router = Router()


async def stop_game(update: "Update", app: "Application"):
    """
    Останавливает игровую сессию
    """
    pass  # TODO: Сделать удаление записи БД из игры
