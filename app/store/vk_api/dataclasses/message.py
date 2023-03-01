from dataclasses import dataclass


@dataclass
class Message:
    peer_id: int
    text: str
