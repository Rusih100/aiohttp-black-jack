from dataclasses import dataclass
from typing import Optional


@dataclass
class Profile:
    id: int
    first_name: str
    last_name: str
    is_admin: Optional[bool] = None
