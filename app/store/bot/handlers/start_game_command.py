import typing

from app.black_jack.game.card import calculate_sum_cards, get_rand_card
from app.black_jack.models import Game, Player
from app.store.bot.answers import BorAnswers
from app.store.bot.commands import BotCommands
from app.store.bot.handlers.utils import ServiceSymbols
from app.store.bot.router import Router
from app.store.bot.states import GameStates
from app.store.vk_api.dataclasses import Button, Keyboard, Message, Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


router = Router()

# TODO: Прокинуть стейт в хэндлер для проверки стейта под капотом
# TODO: Сделать логи


@router.handler(commands=[BotCommands.START_GAME.value.command])
async def start_game(update: "Update", app: "Application") -> None:
    """
    Создает игровую сессию, если она уже не создана.
    Спрашивает сколько игроков будет играть
    """
    chat_id = update.object.message.peer_id

    # Проверяем идет ли игра
    id_game_exist = await app.store.game.get_game_by_chat_id(chat_id=chat_id)

    # Если игра уже идет, выходим
    if id_game_exist is not None:
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
            text=BorAnswers.BOT_NOT_ADMIN,
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
async def wait_number_of_players(update: "Update", app: "Application") -> None:
    """
    Ожидает количество игроков для игры, как только получает, меняет стейт и вызывает следующий хэндлер
    """
    game = await app.store.game.get_game_by_chat_id(
        chat_id=update.object.message.peer_id
    )

    if game is None or game.state.type != GameStates.WAITING_NUMBER_OF_PLAYERS:
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

    # TODO: Транзакция

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

    return await invite_players_to_game(update, app)


async def invite_players_to_game(update: "Update", app: "Application") -> None:
    """
    Рассылает клавиатуру с опросом, будет ли пользователь играть
    """

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
async def handle_new_players(update: "Update", app: "Application") -> None:
    """
    Действие, если пользователь согласился играть
    """

    game = await app.store.game.get_game_by_chat_id(
        chat_id=update.object.message.peer_id
    )

    if game is None or game.state.type != GameStates.INVITING_PLAYERS:
        return

    if game.state.join_players_count >= game.state.players_count:
        return

    # Проверка на наличие игрока
    is_player_exists = await _get_player_from_game(
        vk_id=update.object.message.from_id, game=game
    )

    if is_player_exists is not None:
        message_text = f"{is_player_exists.user.first_name} {is_player_exists.user.last_name} ты уже в игре"
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
    message = Message(peer_id=update.object.message.peer_id, text=message_text)
    await app.store.vk_api.send_message(message)

    if game.state.join_players_count + 1 == game.state.players_count:
        # Обновляем стейт
        await app.store.game.update_state_type(
            game_id=game.game_id, state_type=GameStates.PLAYERS_ARE_PLAYING
        )
        # Переход на следующий этап
        return await start_game_for_players(update, app)


@router.handler(buttons_payload=["invite_keyboard_no"])
async def handle_rejected_players(update: "Update", app: "Application") -> None:
    """
    Действие, если пользователь отказался играть
    """
    return  # TODO: Сделать отказ от игры


async def start_game_for_players(update: "Update", app: "Application") -> None:
    """
    Рассылает клавиатуру с кнопками для игры
    """

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
        peer_id=update.object.message.peer_id, text="Отлично, начинаем!"
    )
    await app.store.vk_api.send_message(message, keyboard)


@router.handler(buttons_payload=["game_players_hit"])
async def handle_game_players_hit(update: "Update", app: "Application") -> None:
    """
    Игрок берет карту
    """

    game = await app.store.game.get_game_by_chat_id(
        chat_id=update.object.message.peer_id
    )

    if game is None or game.state.type != GameStates.PLAYERS_ARE_PLAYING:
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
        message_text = (
            f"{player.user.first_name} {player.user.last_name} больше не берет"
        )
        message = Message(
            peer_id=update.object.message.peer_id, text=message_text
        )
        await app.store.vk_api.send_message(message)
        await app.store.game.set_finish_for_player(player_id=player.player_id)

        if game.state.finished_players_count + 1 == game.state.players_count:
            # Обновляем стейт
            await app.store.game.update_state_type(
                game_id=game.game_id, state_type=GameStates.DEALER_ARE_PLAYING
            )
            # Переход на следующий этап
            return await start_game_for_dealer(update, app)


@router.handler(buttons_payload=["game_players_stand"])
async def handle_game_players_stand(
    update: "Update", app: "Application"
) -> None:
    """
    Игрок отказался брать карту
    """

    game = await app.store.game.get_game_by_chat_id(
        chat_id=update.object.message.peer_id
    )

    if game is None or game.state.type != GameStates.PLAYERS_ARE_PLAYING:
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

    if game.state.finished_players_count + 1 == game.state.players_count:
        # Обновляем стейт
        await app.store.game.update_state_type(
            game_id=game.game_id, state_type=GameStates.DEALER_ARE_PLAYING
        )
        # Переход на следующий этап
        return await start_game_for_dealer(update, app)


async def start_game_for_dealer(update: "Update", app: "Application") -> None:
    """
    Игра дилера и завершение игры
    """
    game = await app.store.game.get_game_by_chat_id(
        chat_id=update.object.message.peer_id
    )

    # Игра дилера

    message = Message(
        peer_id=update.object.message.peer_id, text="🗿 В игру вступает дилер"
    )
    await app.store.vk_api.send_message(message)

    dealer_cards = []
    while (dealer_cards_sum := calculate_sum_cards(dealer_cards)) < 17:
        card = get_rand_card()
        dealer_cards.append(card)

        message_text = f"Дилер берет карту {card}"
        message = Message(
            peer_id=update.object.message.peer_id, text=message_text
        )
        await app.store.vk_api.send_message(message)

    message_text = f"Сумма карт дилера: {dealer_cards_sum}"
    message = Message(peer_id=update.object.message.peer_id, text=message_text)
    await app.store.vk_api.send_message(message)

    # Подводим итоги

    message_text = f"Результаты игры: {ServiceSymbols.LINE_BREAK * 2}"
    for player in game.players:
        player_card_sum = calculate_sum_cards(player.hand)

        if dealer_cards_sum < player_card_sum <= 21:
            player_status = "обыграл дилера 😎"
        elif player_card_sum == dealer_cards_sum and player_card_sum <= 21:
            player_status = "пуш 😐"
        else:
            player_status = "проиграл дилеру 😭"

        message_text += (
            f"⭐ {player.user.first_name} {player.user.last_name}: {ServiceSymbols.LINE_BREAK}"
            f"Cумма очков: {player_card_sum} {ServiceSymbols.LINE_BREAK}"
            f"Статус: {player_status} {ServiceSymbols.LINE_BREAK * 2}"
        )
    message = Message(peer_id=update.object.message.peer_id, text=message_text)
    await app.store.vk_api.send_message(message)

    await app.store.game.close_game(chat_id=update.object.message.peer_id)

    message = Message(
        peer_id=update.object.message.peer_id,
        text=f"Сыграем еще? {BotCommands.START_GAME.value.command}",
    )
    await app.store.vk_api.send_message(message)
