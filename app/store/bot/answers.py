from enum import StrEnum


class BotAnswers(StrEnum):
    BOT_NOT_ADMIN = (
        "Для коректной работы бота нужно сделать бота администратором чата"
    )
    BLACKJACK = "🔥 Blackjack 🔥"
    GAME_END_PUSH = "пуш 😐"
    GAME_END_WON = "обыграл дилера 😎"
    GAME_END_LOST = "проиграл дилеру 😭"
    GAME_END_BLACKJACK = "Blackjack 🔥"
    GAME_END_BUST = "перебор 🗿"
