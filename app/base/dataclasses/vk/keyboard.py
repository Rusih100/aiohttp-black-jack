import json
from dataclasses import dataclass
from typing import List

from marshmallow import Schema, fields


@dataclass
class Action:
    type: str
    payload: str

    @staticmethod
    def make_payload(payload: str) -> str:
        return json.dumps({"button": payload})


@dataclass
class TextAction(Action):
    label: str


@dataclass
class Button:
    action: "Action"
    color: str = "secondary"

    @classmethod
    def TextButton(
        cls, label: str, payload: str, color: str = "secondary"
    ) -> "Button":
        return cls(
            action=TextAction(
                label=label, payload=Action.make_payload(payload), type="text"
            ),
            color=color,
        )


@dataclass
class Keyboard:
    one_time: bool
    buttons: List[List["Button"]]
    inline: bool

    @property
    def json(self):
        return KeyboardSchema().dumps(self)


class ActionSchema(Schema):
    label = fields.Str()
    payload = fields.Str()
    type = fields.Str()
    link = fields.URL()
    hash = fields.Str()
    app_id = fields.Int()
    owner_id = fields.Int()


class ButtonSchema(Schema):
    action = fields.Nested(ActionSchema())
    color = fields.Str()


class KeyboardSchema(Schema):
    one_time = fields.Bool()
    buttons = fields.List(fields.Nested(ButtonSchema(many=True)))
    inline = fields.Bool()
