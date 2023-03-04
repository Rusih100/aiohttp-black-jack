from dataclasses import dataclass
from typing import List

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.store.bot.states import GameStates
from app.store.database.sqlalchemy_base import db


@dataclass
class Chat:
    chat_id: int
    title: str


@dataclass
class Game:
    game_id: int
    chat_id: int
    dealer_id: int
    state: GameStates
    players_count: int
    deck: List["Card"]
    chat: "Chat"
    players: List["Player"]
    dealer: "Dealer"
    current_player_id: int | None = None


@dataclass
class Player:
    player_id: int
    game_id: int
    user_id: int
    cash: int
    bet: int
    hand: List["Card"]
    user: "User"


@dataclass
class Dealer:
    dealer_id: int
    game_id: int
    hand: List["Card"]


@dataclass
class User:
    user_id: int
    vk_id: int
    name: str
    is_admin: bool


class ChatModel(db):
    __tablename__ = "chats"

    chat_id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)

    games: List["GameModel"] = relationship("GameModel", back_populates="chat")

    def __repr__(self):
        return f"ChatModel(chat_id={self.chat_id!r}, title={self.title!r})"


class GameModel(db):
    __tablename__ = "games"

    game_id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chats.chat_id"), nullable=False)
    state = Column(Enum(GameStates), nullable=False)
    players_count = Column(Integer, nullable=False)
    current_player_id = Column(
        Integer, ForeignKey("players.player_id", use_alter=True)
    )
    deck = Column(JSON)

    chat: "ChatModel" = relationship("ChatModel", back_populates="games")
    players: List["PlayerModel"] = relationship(
        "PlayerModel", back_populates="game"
    )
    dealer: "DealerModel" = relationship(
        "DealerModel", back_populates="game", uselist=False
    )

    def __repr__(self):
        return f"GameModel(game_id={self.game_id!r}, chat_id={self.chat_id!r})"


class PlayerModel(db):
    __tablename__ = "players"

    player_id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.game_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    cash = Column(Integer)
    bet = Column(Integer)
    hand = Column(JSON)

    game: "GameModel" = relationship("GameModel", back_populates="players")
    user: "UserModel" = relationship("UserModel", back_populates="players")

    def __repr__(self):
        return f"PlayerModel(player_id={self.player_id!r}, game_id={self.game_id!r}, hand={self.hand!r})"


class DealerModel(db):
    __tablename__ = "dealers"

    dealer_id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.game_id"), nullable=False)
    hand = Column(JSON)

    game: "GameModel" = relationship("GameModel", back_populates="dealer")

    def __repr__(self):
        return f"DealerModel(dealer_id={self.dealer_id!r}, game_id={self.game_id!r}, hand={self.hand!r})"


class UserModel(db):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    vk_id = Column(Integer, nullable=False)
    name = Column(Text, nullable=False)
    is_admin = Column(Boolean, nullable=False)

    players: List["PlayerModel"] = relationship(
        "PlayerModel", back_populates="user"
    )

    def __repr__(self):
        return (
            f"UserModel(user_id={self.user_id!r}, vk_id={self.vk_id!r}, "
            f"name={self.name!r}, is_admin={self.is_admin!r})"
        )
