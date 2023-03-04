import typing
from dataclasses import dataclass
from enum import Enum, StrEnum

from app.store.bot.router import Router
from app.store.vk_api.dataclasses import Message, Update

if typing.TYPE_CHECKING:
    from app.web.app import Application

router = Router()


@dataclass
class Command:
    command: str
    description: str


class BotCommands(Enum):
    START = Command(
        command="/start", description="Запускает бота и отправляет приветствие."
    )
    HELP = Command(
        command="/help", description="Выдает список всех команд бота."
    )
    START_GAME = Command(
        command="/start_game", description="Запускает игровую сессию."
    )
    STOP_GAME = Command(
        command="/stop_game", description="Останавливает игровую сесиию."
    )


class ServiceSymbols(StrEnum):
    LINE_BREAK = "%0A"  # Перенос строки


@router.message_handler(commands=[BotCommands.HELP.value.command])
async def help_command(update: "Update", app: "Application"):
    message_text = f"Список команд бота: {ServiceSymbols.LINE_BREAK}"
    for command in BotCommands:
        message_text += f"{command.value.command} - {command.value.description} {ServiceSymbols.LINE_BREAK}"

    message = Message(peer_id=update.object.message.peer_id, text=message_text)

    await app.store.vk_api.send_message(message=message)
