import typing

from app.store.bot.commands import BotCommands
from app.store.bot.handlers.utils import ServiceSymbols
from app.store.bot.router import Router
from app.store.vk_api.dataclasses import Message, Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


router = Router()


@router.handler(commands=[BotCommands.HELP.value.command])
async def help_command(update: "Update", app: "Application"):
    """
    Отправляет список команд бота
    """
    message_text = f"Список команд бота: {ServiceSymbols.LINE_BREAK}"
    for command in BotCommands:
        message_text += f"{command.value.command} - {command.value.description} {ServiceSymbols.LINE_BREAK}"

    message = Message(peer_id=update.object.message.peer_id, text=message_text)
    await app.store.vk_api.send_message(message=message)
