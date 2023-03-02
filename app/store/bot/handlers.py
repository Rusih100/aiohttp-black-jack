import typing

from app.store.bot.router import Router
from app.store.vk_api.dataclasses import Message, Update

if typing.TYPE_CHECKING:
    from app.web.app import Application

router = Router()


# FIXME: Тестовые хэндлеры
# TODO: Написать нормальные хэндлеры


@router.message_handler(commands=["/start"])
async def start_handler(update: "Update", app: "Application"):
    await app.store.vk_api.send_message(
        Message(
            peer_id=update.object.message.peer_id,
            text="Отработала команда старт",
        )
    )


@router.message_handler(func=lambda update: update.object.message.text == "123")
async def func_handler(update: "Update", app: "Application"):
    await app.store.vk_api.send_message(
        Message(
            peer_id=update.object.message.peer_id,
            text="123",
        )
    )


@router.message_handler()
async def other_message_handler(update: "Update", app: "Application"):
    await app.store.vk_api.send_message(
        Message(
            peer_id=update.object.message.peer_id,
            text="Моя твоя не понимать",
        )
    )
