from dataclasses import dataclass
from typing import Optional


@dataclass
class Message:
    peer_id: int
    text: str
    conversation_message_id: Optional[int] = None
