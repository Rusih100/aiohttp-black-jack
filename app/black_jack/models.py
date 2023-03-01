from dataclasses import dataclass
from typing import List, Union

from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship

from app.store.database.sqlalchemy_base import db


@dataclass
class Chat:
    chat_id: int
    title: str


@dataclass
class Game:
    game_id: int
    chat_id: int
    dealer_id = int
    state: str
    players_count: int
    deck: List["Card"]
    current_player_id: Union[int, None] = None


@dataclass
class Player:
    player_id: int
    game_id: int
    user_id: int
    cash: int
    bet: int
    hand: List["Card"]


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

    chat_id: Mapped[int] = Column(Integer, primary_key=True, nullable=False)
    title: Mapped[str] = Column(Text, nullable=False)

    def __repr__(self):
        return f"ChatModel(chat_id={self.chat_id!r}, title={self.title!r})"


class GameModel(db):
    __tablename__ = "games"

    game_id: Mapped[int] = Column(
        Integer, primary_key=True, nullable=False, autoincrement=True
    )
    chat_id: Mapped[int] = Column(
        Integer, ForeignKey("chats.chat_id"), nullable=False
    )
    state: Mapped[str] = Column(String(length=50), nullable=False)
    players_count: Mapped[int] = Column(Integer, nullable=False)
    current_player_id: Mapped[int] = Column(
        Integer, ForeignKey("players.player_id", use_alter=True)
    )
    deck = Column(JSON)

    players: Mapped[List["PlayerModel"]] = relationship(
        "PlayerModel", back_populates="game"
    )

    def __repr__(self):
        return f"GameModel(game_id={self.game_id!r}, chat_id={self.chat_id!r}, state={self.state!r})"


class PlayerModel(db):
    __tablename__ = "players"

    player_id: Mapped[int] = Column(
        Integer, primary_key=True, nullable=False, autoincrement=True
    )
    game_id: Mapped[int] = Column(
        Integer, ForeignKey("games.game_id"), nullable=False
    )
    user_id: Mapped[int] = Column(
        Integer, ForeignKey("users.user_id"), nullable=False
    )
    cash: Mapped[int] = Column(Integer)
    bet: Mapped[int] = Column(Integer)
    hand = Column(JSON)

    game: Mapped["GameModel"] = relationship(
        "GameModel", back_populates="players"
    )

    def __repr__(self):
        return f"PlayerModel(player_id={self.player_id!r}, game_id={self.game_id!r}, hand={self.hand!r})"


class DealerModel(db):
    __tablename__ = "dealers"

    dealer_id: Mapped[int] = Column(
        Integer, primary_key=True, nullable=False, autoincrement=True
    )
    game_id: Mapped[int] = Column(
        Integer, ForeignKey("games.game_id"), nullable=False
    )
    hand = Column(JSON)

    def __repr__(self):
        return f"DealerModel(dealer_id={self.dealer_id!r}, game_id={self.game_id!r}, hand={self.hand!r})"


class UserModel(db):
    __tablename__ = "users"

    user_id: Mapped[int] = Column(
        Integer, primary_key=True, nullable=False, autoincrement=True
    )
    vk_id: Mapped[int] = Column(Integer, nullable=False)
    name: Mapped[str] = Column(Text, nullable=False)
    is_admin: Mapped[bool] = Column(Boolean, nullable=False)

    def __repr__(self):
        return (
            f"UserModel(user_id={self.user_id!r}, vk_id={self.vk_id!r}, "
            f"name={self.name!r}, is_admin={self.is_admin!r})"
        )
