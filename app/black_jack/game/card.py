from dataclasses import dataclass
from random import choice
import json


def get_rand_card() -> "Card":
    suit = choice(_all_base_suit)
    card = choice(_all_base_cards)
    return Card(**suit, **card)


@dataclass
class Card:
    type: str
    type_name: str
    suit: str
    suit_name: str
    value: int

    @property
    def to_json(self) -> str:
        return json.dumps(
            {
                "type": self.type,
                "type_name": self.type_name,
                "suit": self.suit,
                "suit_name": self.suit_name,
                "value": self.value
            }
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Card":
        return Card(
            **json.loads(json_str)
        )


_all_base_suit = [
    {"suit": "Clubs", "suit_name": "Трефы"},
    {"suit": "Diamonds", "suit_name": "Бубны"},
    {"suit": "Hearts", "suit_name": "Червы"},
    {"suit": "Spades", "suit_name": "Пики"},
]

_all_base_cards = [
    {"type": "Ace", "type_name": "Туз", "value": 11},
    {"type": "King", "type_name": "Король", "value": 10},
    {"type": "Queen", "type_name": "Туз", "value": 10},
    {"type": "Ace", "type_name": "Туз", "value": 10},
    {"type": "Number", "type_name": "10", "value": 10},
    {"type": "Number", "type_name": "9", "value": 9},
    {"type": "Number", "type_name": "8", "value": 8},
    {"type": "Number", "type_name": "7", "value": 7},
    {"type": "Number", "type_name": "6", "value": 6},
    {"type": "Number", "type_name": "5", "value": 5},
    {"type": "Number", "type_name": "4", "value": 4},
    {"type": "Number", "type_name": "3", "value": 3},
    {"type": "Number", "type_name": "2", "value": 2},
]
