import typing

from app.store.bot.commands import BotCommands
from app.store.bot.router import Router
from app.store.bot.states import GameStates
from app.store.vk_api.dataclasses import Button, Keyboard, Message, Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


router = Router()


@router.handler(commands=[BotCommands.START_GAME.value.command])
async def start_game(update: "Update", app: "Application"):
    """
    Создает игровую сессию, если она уже не создана.
    Спрашивает сколько игроков будет играть
    """
    chat_id = update.object.message.peer_id

    # Проверяем идет ли игра
    check_game = await app.store.game.get_game_by_chat_id(chat_id=chat_id)

    # Если игра уже идет, выходим
    if check_game is not None:
        message_text = f"Игра уже идет"
        message = Message(
            peer_id=update.object.message.peer_id, text=message_text
        )
        await app.store.vk_api.send_message(message=message)
        return

    # Получаем список участников чата
    profiles = await app.store.vk_api.get_conversation_members(
        update.object.message
    )

    if not profiles:
        message_text = (
            f"Для коректной работы бота нужно сделать бота администратором чата"
        )
        message = Message(
            peer_id=update.object.message.peer_id, text=message_text
        )
        await app.store.vk_api.send_message(message=message)
        return

    # Если игра не идет, создаем новую
    await app.store.game.init_game(chat_id=chat_id, profiles=profiles)

    # Выдаем приглашение
    message_text = f"Сколько человек будет играть?"
    message = Message(peer_id=update.object.message.peer_id, text=message_text)
    await app.store.vk_api.send_message(message=message)


def _validate_int(update: Update) -> bool:
    text = update.object.message.text
    try:
        num = int(text)
    except (ValueError, TypeError):
        return False
    if num <= 0:
        return False
    return True


# В хэдлер прилетят все сообщения содержащие только целые числа, далее проверим стейт
@router.handler(func=_validate_int)
async def waiting_number_of_players(update: "Update", app: "Application"):
    """
    Ожидает количество игроков для игры, как только получает, меняет стейт и вызывает следующий хэндлер
    """
    pass  # TODO


async def invite_keyboard(update: "Update", app: "Application"):
    """
    Рассылает клавиатуру с опросом, будет ли пользователь играть
    """

    message = Message(
        peer_id=update.object.message.peer_id, text="Начинаем игру"
    )
    await app.store.vk_api.send_message(message)

    # TODO: Доделать рассылку для всех игроков
    keyboard = Keyboard(
        one_time=False,
        inline=False,
        buttons=[
            [
                Button.TextButton("Да буду!", "invite_keyboard_yes"),
                Button.TextButton("Нет", "invite_keyboard_no"),
            ]
        ],
    )
    message = Message(
        peer_id=update.object.message.peer_id, text="Будешь играть?"
    )
    await app.store.vk_api.send_message(message, keyboard)


@router.handler(buttons_payload=["invite_keyboard_yes"])
async def invite_keyboard_yes(update: "Update", app: "Application"):
    """
    Действие, если пользователь согласился играть
    """
    # TODO: Логика добавления игрока

    message = Message(peer_id=update.object.message.peer_id, text=f"Отлично")
    await app.store.vk_api.send_message(message)


@router.handler(buttons_payload=["invite_keyboard_no"])
async def invite_keyboard_no(update: "Update", app: "Application"):
    """
    Действие, если пользователь отказался играть
    """
    pass
