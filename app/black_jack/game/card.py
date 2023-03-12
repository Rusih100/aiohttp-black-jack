from dataclasses import dataclass
from random import choice
from typing import List


def get_rand_card() -> "Card":
    suit = choice(_all_base_suit)
    card = choice(_all_base_cards)
    return Card(**suit, **card)


def calculate_sum_cards(cards: List["Card"]) -> int:
    ace_cards = []
    other_cards = []
    for card in cards:
        if card.type == "Ace":
            ace_cards.append(card.value)
        else:
            other_cards.append(card.value)

    result = sum(other_cards)
    for value in ace_cards:
        result += 1 if result > 21 else value

    return result


@dataclass
class Card:
    type: str
    type_name: str
    suit: str
    suit_name: str
    value: int

    @property
    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "type_name": self.type_name,
            "suit": self.suit,
            "suit_name": self.suit_name,
            "value": self.value,
        }

    def __str__(self):
        return f"{_emoji_suit[self.suit]} {self.type_name} {self.suit_name}"


_emoji_suit = {"Clubs": "♣️", "Diamonds": "♦️", "Hearts": "♥️", "Spades": "♠️"}

_all_base_suit = [
    {"suit": "Clubs", "suit_name": "Трефы"},
    {"suit": "Diamonds", "suit_name": "Бубны"},
    {"suit": "Hearts", "suit_name": "Червы"},
    {"suit": "Spades", "suit_name": "Пики"},
]

_all_base_cards = [
    {"type": "Ace", "type_name": "Туз", "value": 11},
    {"type": "King", "type_name": "Король", "value": 10},
    {"type": "Queen", "type_name": "Дама", "value": 10},
    {"type": "Jack", "type_name": "Валет", "value": 10},
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
