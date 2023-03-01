from dataclasses import dataclass
from typing import List, Union

from sqlalchemy import BigInteger, Column, String
from app.store.database.sqlalchemy_base import db

from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Boolean,
    ForeignKey,
    JSON
)


@dataclass
class Chat:
    chat_id: int
    title: str


@dataclass
class Game:
    game_id: int
    chat_id: int
    state: str
    players_count: int
    deck: List['Card']
    current_player_id: Union[int, None] = None


class ChatModel(db):
    __tablename__ = "chats"

    chat_id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)

    def __repr__(self):
        return f'ChatModel(chat_id={self.chat_id!r}, title={self.title!r})'


class GameModel(db):
    __tablename__ = "games"

    game_id = Column(Integer, primary_key=True, nullable=False)
    chat_id = Column(Integer, ForeignKey('chats.chat_id'), nullable=False)
    state = Column(String(length=250), nullable=False)
    players_count = Column(Integer, nullable=False)
    deck = Column(JSON)
    current_player_id = Column(Integer, ForeignKey('players.player_id'))

    def __repr__(self):
        return f'GameModel(game_id={self.game_id!r}, chat_id={self.chat_id!r}, state={self.state!r})'


