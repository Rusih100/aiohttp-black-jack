from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy import JSON, Boolean, Column, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.store.bot.states import GameStates
from app.store.database.sqlalchemy_base import db


@dataclass
class Chat:
    chat_id: int

    @classmethod
    def from_sqlalchemy(cls, model: "ChatModel") -> "Chat":
        return cls(chat_id=model.chat_id)


@dataclass
class Card:
    pass


@dataclass
class Game:
    game_id: int
    chat_id: int
    players_count: int
    chat: "Chat"
    players: List["Player"]
    state: Optional["State"]

    @classmethod
    def from_sqlalchemy(cls, model: "GameModel") -> "Game":
        return cls(
            game_id=model.game_id,
            chat_id=model.chat_id,
            players_count=model.players_count,
            chat=Chat.from_sqlalchemy(model.chat),
            players=[
                Player.from_sqlalchemy(player) for player in model.players
            ],
            state=State.from_sqlalchemy(model.state) if model.state else None,
        )


@dataclass
class State:
    state_id: int
    game_id: int
    type: GameStates
    deck: List["Card"]
    current_player_id: Optional[int] = None
    current_player: Optional["Player"] = None

    @classmethod
    def from_sqlalchemy(cls, model: "StateModel") -> "State":
        return cls(
            state_id=model.state_id,
            game_id=model.state_id,
            type=model.type,
            deck=model.deck,  # TODO: Сделать преобразование карт из JSON
            current_player_id=model.current_player_id
            if model.current_player_id
            else None,
            current_player=Player.from_sqlalchemy(model.current_player)
            if model.current_player
            else None,
        )


@dataclass
class Player:
    player_id: int
    game_id: int
    user_id: int
    cash: int
    bet: int
    hand: List["Card"]
    user: "User"

    @classmethod
    def from_sqlalchemy(cls, model: "PlayerModel") -> "Player":
        return cls(
            player_id=model.player_id,
            game_id=model.game_id,
            user_id=model.user_id,
            cash=model.cash,
            bet=model.bet,
            hand=model.hand,  # TODO: Сделать преобразование карт из JSON
            user=model.user,
        )


@dataclass
class User:
    user_id: int
    vk_id: int
    first_name: str
    last_name: str
    is_admin: bool

    @classmethod
    def from_sqlalchemy(cls, model: "UserModel") -> "User":
        return cls(
            user_id=model.user_id,
            vk_id=model.vk_id,
            first_name=model.first_name,
            last_name=model.last_name,
            is_admin=model.is_admin,
        )


class ChatModel(db):
    __tablename__ = "chats"

    chat_id = Column(Integer, primary_key=True)

    games: List["GameModel"] = relationship("GameModel", back_populates="chat")

    def __repr__(self):
        return f"ChatModel(chat_id={self.chat_id!r}, title={self.title!r})"


class GameModel(db):
    __tablename__ = "games"

    game_id = Column(Integer, primary_key=True)
    chat_id = Column(
        Integer, ForeignKey("chats.chat_id"), nullable=False, index=True
    )
    players_count = Column(Integer, nullable=False)

    state: "StateModel" = relationship(
        "StateModel", back_populates="game", uselist=False, lazy="joined"
    )
    chat: "ChatModel" = relationship(
        "ChatModel", back_populates="games", lazy="joined"
    )
    players: List["PlayerModel"] = relationship(
        "PlayerModel", back_populates="game", lazy="joined"
    )

    def __repr__(self):
        return f"GameModel(game_id={self.game_id!r}, chat_id={self.chat_id!r})"


class StateModel(db):
    __tablename__ = "states"

    state_id = Column(Integer, primary_key=True)
    game_id = Column(
        Integer, ForeignKey("games.game_id"), nullable=False, index=True
    )
    type = Column(Enum(GameStates), nullable=False)
    deck = Column(JSON)
    current_player_id = Column(Integer, ForeignKey("players.player_id"))

    current_player: "PlayerModel" = relationship(
        "PlayerModel", back_populates="state", lazy="joined"
    )
    game: "GameModel" = relationship("GameModel", back_populates="state")


class PlayerModel(db):
    __tablename__ = "players"

    player_id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey("games.game_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    cash = Column(Integer)
    bet = Column(Integer)
    hand = Column(JSON)

    game: "GameModel" = relationship("GameModel", back_populates="players")
    state: "StateModel" = relationship(
        "StateModel", back_populates="current_player"
    )
    user: "UserModel" = relationship(
        "UserModel", back_populates="players", lazy="joined"
    )

    def __repr__(self):
        return f"PlayerModel(player_id={self.player_id!r}, game_id={self.game_id!r}, hand={self.hand!r})"


class UserModel(db):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    vk_id = Column(Integer, nullable=False)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    is_admin = Column(Boolean, nullable=False)

    players: List["PlayerModel"] = relationship(
        "PlayerModel", back_populates="user"
    )

    def __repr__(self):
        return (
            f"UserModel(user_id={self.user_id!r}, vk_id={self.vk_id!r}, "
            f"name={self.name!r}, is_admin={self.is_admin!r})"
        )
