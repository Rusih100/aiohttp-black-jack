from dataclasses import dataclass
from hashlib import sha256
from typing import Optional

from sqlalchemy import BigInteger, Column, String

from app.store.database.sqlalchemy_base import db


@dataclass
class Admin:
    id: int
    email: str
    password: Optional[str] = None

    def is_password_valid(self, password: str):
        return self.password == self.password_to_hash(password)

    @staticmethod
    def password_to_hash(password: str) -> str:
        return sha256(password.encode()).hexdigest()

    @classmethod
    def from_session(cls, session: Optional[dict]) -> Optional["Admin"]:
        return cls(id=session["admin"]["id"], email=session["admin"]["email"])

    @classmethod
    def from_sqlalchemy(cls, model: "AdminModel") -> "Admin":
        return cls(id=model.id, email=model.email, password=model.password)


class AdminModel(db):
    __tablename__ = "admins"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(length=64), index=True, unique=True, nullable=False)
    password = Column(String(length=64), nullable=False)

    def __repr__(self):
        return f"AdminModel(id={self.id!r}, email={self.email!r})"
