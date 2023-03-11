import typing

from app.store.bot.commands import BotCommands
from app.store.bot.handlers.utils import ServiceSymbols
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
        message = Message(
            peer_id=update.object.message.peer_id, text="Игра уже идет"
        )
        await app.store.vk_api.send_message(message=message)
        return

    # Получаем список участников чата
    profiles = await app.store.vk_api.get_conversation_members(
        message=update.object.message
    )

    if not profiles:
        message = Message(
            peer_id=update.object.message.peer_id,
            text="Для коректной работы бота нужно сделать бота администратором чата",
        )
        await app.store.vk_api.send_message(message=message)
        return

    # Если игра не идет, создаем новую
    await app.store.game.init_game(chat_id=chat_id, profiles=profiles)

    # Выдаем приглашение
    message = Message(
        peer_id=update.object.message.peer_id,
        text="Сколько человек будет играть?",
    )
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
    game = await app.store.game.get_game_by_chat_id(
        chat_id=update.object.message.peer_id
    )

    if game.state.type != GameStates.WAITING_NUMBER_OF_PLAYERS:
        return

    number_of_players = int(update.object.message.text)

    # Получаем список участников чата
    profiles = await app.store.vk_api.get_conversation_members(
        message=update.object.message
    )

    if len(profiles) < number_of_players:
        message_text = (
            f"Введенное количество игроков больше чем участников чата. {ServiceSymbols.LINE_BREAK}"
            f"Повторите ввод"
        )
        message = Message(
            peer_id=update.object.message.peer_id, text=message_text
        )
        await app.store.vk_api.send_message(message=message)
        return

    # Обновляем количество игроков
    await app.store.game.update_players_count(
        game_id=game.game_id, players_count=number_of_players
    )

    # Обновляем стейт
    await app.store.game.update_state_type(
        game_id=game.game_id, state_type=GameStates.INVITING_PLAYERS
    )

    message = Message(peer_id=update.object.message.peer_id, text="Принял")
    await app.store.vk_api.send_message(message=message)

    return await inviting_players(update, app)


async def inviting_players(update: "Update", app: "Application"):
    """
    Рассылает клавиатуру с опросом, будет ли пользователь играть
    """

    # Нужна ли тут проверка стейта? Думаю нет

    keyboard = Keyboard(
        one_time=False,
        inline=False,
        buttons=[
            [
                Button.TextButton("Я буду!", "invite_keyboard_yes"),
                Button.TextButton("Я не буду", "invite_keyboard_no"),
            ]
        ],
    )
    message = Message(
        peer_id=update.object.message.peer_id, text="Кто будет играть?"
    )
    await app.store.vk_api.send_message(message, keyboard)


@router.handler(buttons_payload=["invite_keyboard_yes"])
async def inviting_players_yes(update: "Update", app: "Application"):
    """
    Действие, если пользователь согласился играть
    """

    game = await app.store.game.get_game_by_chat_id(
        chat_id=update.object.message.peer_id
    )

    if game.state.type != GameStates.INVITING_PLAYERS:
        return

    # Добавляем игрока
    if game.join_players_count < game.players_count:
        # Проверка на наличие игрока
        check_player = await app.store.game.get_player_by_game_id_and_vk_id(
            game_id=game.game_id, vk_id=update.object.message.from_id
        )
        if check_player is not None:
            message_text = f"{check_player.user.first_name} {check_player.user.last_name}, ты уже добавлен."
            message = Message(
                peer_id=update.object.message.peer_id, text=message_text
            )
            await app.store.vk_api.send_message(message)
            return

        # Добавляем игрока
        player = await app.store.game.create_player(
            game_id=game.game_id, vk_id=update.object.message.from_id
        )
        message_text = (
            f"{player.user.first_name} {player.user.last_name}, ты добавлен."
        )
        message = Message(
            peer_id=update.object.message.peer_id, text=message_text
        )
        await app.store.vk_api.send_message(message)

        if game.join_players_count + 1 == game.players_count:
            message = Message(
                peer_id=update.object.message.peer_id,
                text="Отлично, начинанаем!",
            )
            await app.store.vk_api.send_message(message)
            # TODO: Смена стейта
            # Переход на следующий этап
            return


@router.handler(buttons_payload=["invite_keyboard_no"])
async def inviting_players_no(update: "Update", app: "Application"):
    """
    Действие, если пользователь отказался играть
    """
    return
