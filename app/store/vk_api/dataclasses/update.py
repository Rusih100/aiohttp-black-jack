import json
from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class Update:
    type: str
    object: Union["ObjectMessageNew", None]
    group_id: int

    @classmethod
    def parse_update(cls, raw_update) -> Union["Update", None]:
        update_type = raw_update["type"]
        raw_update_object = raw_update["object"]

        if update_type == "message_new":
            update_object = ObjectMessageNew.parse_object(raw_update_object)
        else:
            return None

        return cls(
            type=raw_update["type"],
            group_id=raw_update["group_id"],
            object=update_object,
        )


# Object type: message_new


@dataclass
class ObjectMessageNew:
    message: "UpdateMessage"

    @classmethod
    def parse_object(cls, raw_update_object) -> "ObjectMessageNew":
        message: dict = raw_update_object["message"]

        raw_payload = message.get("payload", None)

        if raw_payload:
            payload_json = json.loads(raw_payload)
            payload = Payload(
                button=payload_json.get("button", None),
                command=payload_json.get("command", None),
            )
        else:
            payload = None

        return cls(
            message=UpdateMessage(
                id=message["id"],
                date=message["date"],
                peer_id=message["peer_id"],
                from_id=message["from_id"],
                text=message["text"],
                conversation_message_id=message["conversation_message_id"],
                payload=payload,
            )
        )


@dataclass
class UpdateMessage:
    id: int
    date: int
    peer_id: int
    from_id: int
    text: str
    conversation_message_id: int

    payload: Optional["Payload"]


@dataclass
class Payload:
    button: Optional[str]
    command: Optional[str]
