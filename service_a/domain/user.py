from dataclasses import dataclass
@dataclass(frozen=True)
class User:
    id: int | None
    name: str
    email: str
    password_hash: str
