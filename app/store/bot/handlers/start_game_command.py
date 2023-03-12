import typing

from app.black_jack.game.card import Card, get_rand_card, calculate_sum_cards
from app.black_jack.models import Game, Player
from app.store.bot.commands import BotCommands
from app.store.bot.handlers.utils import ServiceSymbols
from app.store.bot.router import Router
from app.store.bot.states import GameStates
from app.store.vk_api.dataclasses import Button, Keyboard, Message, Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


router = Router()

# TODO: Прокинуть стейт в хэндлер для проверки стейта под капотом


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


async def _get_player_from_game(vk_id: int, game: Game) -> Player | None:
    for player in game.players:
        if player.user.vk_id == vk_id:
            return player
    return None


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
    if game.state.join_players_count < game.state.players_count:
        # Проверка на наличие игрока
        check_player = await _get_player_from_game(
            vk_id=update.object.message.from_id, game=game
        )

        if check_player is not None:
            message_text = f"{check_player.user.first_name} {check_player.user.last_name} ты уже в игре"
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
            f"{player.user.first_name} {player.user.last_name} теперь в игре"
        )
        message = Message(
            peer_id=update.object.message.peer_id, text=message_text
        )
        await app.store.vk_api.send_message(message)

        if game.state.join_players_count + 1 == game.state.players_count:
            # Обновляем стейт
            await app.store.game.update_state_type(
                game_id=game.game_id, state_type=GameStates.PLAYERS_ARE_PLAYING
            )
            # Переход на следующий этап
            return await game_players(update, app)


@router.handler(buttons_payload=["invite_keyboard_no"])
async def inviting_players_no(update: "Update", app: "Application"):
    """
    Действие, если пользователь отказался играть
    """
    return  # TODO: Сделать отказ от игры


async def game_players(update: "Update", app: "Application"):
    """
    Рассылает клавиатуру с кнопками для игры
    """

    # Нужна ли тут проверка стейта? Думаю нет

    keyboard = Keyboard(
        one_time=False,
        inline=False,
        buttons=[
            [
                Button.TextButton("Хватит", "game_players_stand"),
                Button.TextButton("Взять карту", "game_players_hit"),
            ]
        ],
    )
    message = Message(
        peer_id=update.object.message.peer_id, text="Отлично, начинанаем!"
    )
    await app.store.vk_api.send_message(message, keyboard)


@router.handler(buttons_payload=["game_players_hit"])
async def game_players_hit(update: "Update", app: "Application"):
    """
    Игрок берет карту
    """

    game = await app.store.game.get_game_by_chat_id(
        chat_id=update.object.message.peer_id
    )

    if game.state.type != GameStates.PLAYERS_ARE_PLAYING:
        return

    player = await _get_player_from_game(
        vk_id=update.object.message.from_id, game=game
    )
    if player is None or player.is_finished:
        return

    # Даем игроку карту

    card = get_rand_card()
    await app.store.game.add_card_for_player(
        player_id=player.player_id, card=card
    )

    player_cards = player.hand
    player_cards.append(card)
    cards_sum = calculate_sum_cards(player_cards)

    message_text = f"{player.user.first_name} {player.user.last_name}, выдаю {card} {ServiceSymbols.LINE_BREAK * 2}"
    message_text += f"Твои карты: {ServiceSymbols.LINE_BREAK}"
    for card in player_cards:
        message_text += f"{card}{ServiceSymbols.LINE_BREAK}"
    message_text += f"{ServiceSymbols.LINE_BREAK}Сумма карт: {cards_sum}"

    message = Message(peer_id=update.object.message.peer_id, text=message_text)
    await app.store.vk_api.send_message(message)

    if cards_sum >= 21:
        message_text = f"{player.user.first_name} {player.user.last_name} больше не берет"
        message = Message(peer_id=update.object.message.peer_id, text=message_text)
        await app.store.vk_api.send_message(message)
        await app.store.game.set_finish_for_player(player_id=player.player_id)

    # TODO: Переход к следующему стейту, если количество игроков достигнуто


@router.handler(buttons_payload=["game_players_stand"])
async def game_players_stand(update: "Update", app: "Application"):
    """
    Игрок отказался брать карту
    """

    game = await app.store.game.get_game_by_chat_id(
        chat_id=update.object.message.peer_id
    )

    if game.state.type != GameStates.PLAYERS_ARE_PLAYING:
        return

    player = await _get_player_from_game(
        vk_id=update.object.message.from_id, game=game
    )
    if player is None or player.is_finished:
        return

    # Меняем is_finished у игрока

    await app.store.game.set_finish_for_player(player_id=player.player_id)

    message_text = f"{player.user.first_name} {player.user.last_name} - пасс"
    message = Message(peer_id=update.object.message.peer_id, text=message_text)
    await app.store.vk_api.send_message(message)

    # TODO: Переход к следующему стейту, если количество игроков достигнуто
