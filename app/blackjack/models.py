from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy import JSON, Boolean, Column, Enum, ForeignKey, Integer, Text, BigInteger
from sqlalchemy.orm import relationship

from app.blackjack.game.card import Card
from app.store.bot.states import GameStates
from app.store.database.sqlalchemy_base import db


@dataclass
class Chat:
    chat_id: int

    @classmethod
    def from_sqlalchemy(cls, model: "ChatModel") -> "Chat":
        return cls(chat_id=model.chat_id)


@dataclass
class Game:
    game_id: int
    chat_id: int
    chat: "Chat"
    players: List["Player"]
    state: Optional["State"]

    @classmethod
    def from_sqlalchemy(cls, model: "GameModel") -> "Game":
        return cls(
            game_id=model.game_id,
            chat_id=model.chat_id,
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
    players_count: int
    join_players_count: int
    bet_placed_players_count: int
    finished_players_count: int

    @classmethod
    def from_sqlalchemy(cls, model: "StateModel") -> "State":
        return cls(
            state_id=model.state_id,
            game_id=model.state_id,
            type=model.type,
            players_count=model.players_count,
            join_players_count=model.join_players_count,
            bet_placed_players_count=model.bet_placed_players_count,
            finished_players_count=model.finished_players_count,
        )


@dataclass
class Player:
    player_id: int
    game_id: int
    user_id: int
    cash: int
    bet: int
    is_bet_placed: int
    is_finished: bool
    hand: List["Card"]
    user: "User"

    @staticmethod
    def _parse_hand(hand: dict) -> List["Card"]:
        raw_cards = hand["cards"]
        return [Card(**raw_card) for raw_card in raw_cards]

    @classmethod
    def from_sqlalchemy(cls, model: "PlayerModel") -> "Player":
        return cls(
            player_id=model.player_id,
            game_id=model.game_id,
            user_id=model.user_id,
            cash=model.cash,
            bet=model.bet,
            hand=cls._parse_hand(model.hand),
            user=model.user,
            is_bet_placed=model.is_bet_placed,
            is_finished=model.is_finished,
        )


@dataclass
class User:
    user_id: int
    vk_id: int
    first_name: str
    last_name: str
    is_admin: bool  # FIXME: Относительно чата может быть разным

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

    game: "GameModel" = relationship(
        "GameModel", back_populates="chat", uselist=False
    )

    def __repr__(self):
        return f"ChatModel(chat_id={self.chat_id!r}, title={self.title!r})"


class GameModel(db):
    __tablename__ = "games"

    game_id = Column(Integer, primary_key=True)
    chat_id = Column(
        Integer,
        ForeignKey("chats.chat_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    state: "StateModel" = relationship(
        "StateModel", back_populates="game", uselist=False, lazy="joined"
    )
    chat: "ChatModel" = relationship(
        "ChatModel", back_populates="game", lazy="joined"
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
        Integer,
        ForeignKey("games.game_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    players_count = Column(Integer, nullable=False)
    join_players_count = Column(Integer, nullable=False)
    bet_placed_players_count = Column(Integer, nullable=False)
    finished_players_count = Column(Integer, nullable=False)
    type = Column(Enum(GameStates), nullable=False)

    game: "GameModel" = relationship("GameModel", back_populates="state")

    def __repr__(self):
        return (
            f"StateModel(state_id={self.state_id!r}, game_id={self.game_id!r})"
        )


class PlayerModel(db):
    __tablename__ = "players"

    player_id = Column(Integer, primary_key=True)
    game_id = Column(
        Integer,
        ForeignKey("games.game_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Integer, ForeignKey("users.user_id"), nullable=False, index=True
    )
    is_bet_placed = Column(Boolean, nullable=False)
    is_finished = Column(Boolean, nullable=False)
    cash = Column(BigInteger)
    bet = Column(BigInteger)
    hand = Column(JSON)

    game: "GameModel" = relationship("GameModel", back_populates="players")
    user: "UserModel" = relationship(
        "UserModel", back_populates="players", lazy="joined"
    )

    def __repr__(self):
        return f"PlayerModel(player_id={self.player_id!r}, game_id={self.game_id!r}, hand={self.hand!r})"


class UserModel(db):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    vk_id = Column(Integer, nullable=False, unique=True, index=True)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    is_admin = Column(Boolean, nullable=False)

    players: List["PlayerModel"] = relationship(
        "PlayerModel", back_populates="user"
    )

    def __repr__(self):
        return (
            f"UserModel(user_id={self.user_id!r}, vk_id={self.vk_id!r}, "
            f"first_name={self.first_name!r}, last_name={self.last_name!r}, is_admin={self.is_admin!r})"
        )
