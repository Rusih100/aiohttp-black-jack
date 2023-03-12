import typing

from app.store.bot.commands import BotCommands
from app.store.bot.handlers.utils import ServiceSymbols
from app.store.bot.router import Router
from app.store.vk_api.dataclasses import Message, Update
from app.store.bot.answers import BorAnswers

if typing.TYPE_CHECKING:
    from app.web.app import Application


router = Router()


# TODO: убрать хардкод, прокинув app в lambda
@router.handler(
    func=lambda update: update.object.message.action.type == "chat_invite_user"
    and update.object.message.action.member_id == -218833701
)
async def invite_bot(update: "Update", app: "Application") -> None:
    """
    Вызывает функцию приветствия, когда бота добавили в чат.
    """
    await start_command(update, app)


@router.handler(commands=[BotCommands.START.value.command])
async def start_command(update: "Update", app: "Application") -> None:
    """
    Отправляет приветствие.
    Добавляет чат в БД.
    """
    # Создаем чат в БД
    await app.store.game.create_chat(chat_id=update.object.message.peer_id)

    message_text = (
        f"Привет! Со мной можно сыграть в BlackJack {ServiceSymbols.LINE_BREAK}"
    )
    message = Message(peer_id=update.object.message.peer_id, text=message_text)
    await app.store.vk_api.send_message(message=message)

    message_text = (
        f"Список команд - {BotCommands.HELP.value.command} {ServiceSymbols.LINE_BREAK}"
        f"Чтобы начать игру используй команду {BotCommands.START_GAME.value.command}"
    )
    message = Message(peer_id=update.object.message.peer_id, text=message_text)
    await app.store.vk_api.send_message(message=message)

    message = Message(peer_id=update.object.message.peer_id, text=BorAnswers.BOT_NOT_ADMIN)
    await app.store.vk_api.send_message(message=message)
