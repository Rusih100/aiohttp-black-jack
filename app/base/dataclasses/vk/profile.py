from dataclasses import dataclass


@dataclass
class Profile:
    id: int
    first_name: str
    last_name: str
    is_admin: bool = False
