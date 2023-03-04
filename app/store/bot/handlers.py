import typing
from dataclasses import dataclass
from enum import Enum, StrEnum

from app.store.bot.router import Router
from app.store.vk_api.dataclasses import Message, Update, Keyboard, Button

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


@router.handler(commands=[BotCommands.START.value.command])
async def start_command(update: "Update", app: "Application"):
    """
    Отправляет приветствие.
    """
    # TODO: Сделать по инвайту бота в чат
    # TODO: Получить список пользователей

    message_text = f"Привет! Со мной можно сыграть в BlackJAck {ServiceSymbols.LINE_BREAK}"

    message = Message(peer_id=update.object.message.peer_id, text=message_text)
    await app.store.vk_api.send_message(message=message)

    message_text = f"Список команд - {BotCommands.HELP.value.command} {ServiceSymbols.LINE_BREAK}" \
                   f"Чтобы начать игру используй команду {BotCommands.START_GAME.value.command}"

    message = Message(peer_id=update.object.message.peer_id, text=message_text)
    await app.store.vk_api.send_message(message=message)


@router.handler(commands=[BotCommands.HELP.value.command])
async def help_command(update: "Update", app: "Application"):
    """
    Отправляет список команд бота.
    """
    message_text = f"Список команд бота: {ServiceSymbols.LINE_BREAK}"
    for command in BotCommands:
        message_text += f"{command.value.command} - {command.value.description} {ServiceSymbols.LINE_BREAK}"

    message = Message(peer_id=update.object.message.peer_id, text=message_text)
    await app.store.vk_api.send_message(message=message)


# FIXME: Это заготовки для будущего кода

@router.handler(commands=[BotCommands.START_GAME.value.command])
async def invite_keyboard(update: "Update", app: "Application"):
    """
    Рассылает клавиатуру с опросом, будет ли пользователь играть
    """
    message = Message(
        peer_id=update.object.message.peer_id,
        text="Начинаем игру"
    )
    await app.store.vk_api.send_message(message)

    # TODO: Доделать рассылку для всех игроков
    keyboard = Keyboard(
        one_time=True,
        inline=False,
        buttons=[
            [
                Button.TextButton("Да буду!", "invite_keyboard_yes"),
                Button.TextButton("Нет", "invite_keyboard_no"),
            ]
        ]
    )
    message = Message(
        peer_id=update.object.message.peer_id,
        text="Будешь играть?"
    )
    await app.store.vk_api.send_message(message, keyboard)


@router.handler(buttons_payload=['invite_keyboard_yes'])
async def invite_keyboard_yes(update: "Update", app: "Application"):
    """
    Действие, если пользователь согласился играть
    """

    # TODO: Логика добавления игрока

    message = Message(
        peer_id=update.object.message.peer_id,
        text=f"Отлично"
    )
    await app.store.vk_api.send_message(message)


@router.handler(buttons_payload=['invite_keyboard_no'])
async def invite_keyboard_no(update: "Update", app: "Application"):
    """
    Действие, если пользователь отказался играть
    """
    pass
