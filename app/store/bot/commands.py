from dataclasses import dataclass
from enum import Enum


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
