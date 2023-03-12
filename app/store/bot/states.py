from enum import Enum, auto


class GameStates(Enum):
    WAITING_NUMBER_OF_PLAYERS = auto()
    INVITING_PLAYERS = auto()
    PLAYERS_ARE_PLAYING = auto()
    DEALER_ARE_PLAYING = auto()
