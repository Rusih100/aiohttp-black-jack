import json
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Dict, Optional, Union


class UpdateTypes(StrEnum):
    MESSAGE_NEW = "message_new"


@dataclass
class Update:
    type: str
    object: Optional["ObjectMessageNew"]
    group_id: int

    @classmethod
    def parse_update(cls, raw_update: Dict[str, Any]) -> Union["Update", None]:
        update_type = raw_update.get("type", None)
        update_group_id = raw_update.get("group_id", None)
        raw_update_object = raw_update.get("object", None)

        if not all((update_type, update_group_id, raw_update_object)):
            return None

        if update_type == UpdateTypes.MESSAGE_NEW:
            update_object = ObjectMessageNew.parse_object(raw_update_object)
        else:
            return None

        return cls(
            type=update_type,
            group_id=update_group_id,
            object=update_object,
        )


# Object type: message_new


@dataclass
class ObjectMessageNew:
    message: "UpdateMessage"

    @classmethod
    def parse_object(
        cls, raw_update_object: Dict[str, Any]
    ) -> "ObjectMessageNew":
        message: dict = raw_update_object["message"]

        return cls(
            message=UpdateMessage(
                id=message.get("id", None),
                date=message.get("date", None),
                peer_id=message.get("peer_id", None),
                from_id=message.get("from_id", None),
                text=message.get("text", None),
                conversation_message_id=message.get(
                    "conversation_message_id", None
                ),
                payload=Payload.parse_payload(message),
                action=UpdateMessageAction.parse_action(message),
            )
        )


@dataclass
class UpdateMessage:
    id: Optional[int]
    date: Optional[int]
    peer_id: Optional[int]
    from_id: Optional[int]
    text: Optional[str]
    conversation_message_id: Optional[int]
    payload: Optional["Payload"]
    action: Optional["UpdateMessageAction"]


@dataclass
class UpdateMessageAction:
    type: Optional[str]
    member_id: Optional[int]

    @classmethod
    def parse_action(
        cls, message: Dict[str, Any]
    ) -> Union["UpdateMessageAction", None]:
        action: Dict[str, Any] = message.get("action", None)
        if action:
            return UpdateMessageAction(
                type=action.get("type", None),
                member_id=action.get("member_id", None),
            )
        return None


@dataclass
class Payload:
    button: Optional[str]
    command: Optional[str]

    @classmethod
    def parse_payload(cls, message: Dict[str, Any]) -> Union["Payload", None]:
        raw_payload = message.get("payload", None)
        if raw_payload:
            payload_json = json.loads(raw_payload)
            return Payload(
                button=payload_json.get("button", None),
                command=payload_json.get("command", None),
            )
        return None
