from dataclasses import dataclass
from uuid import UUID


@dataclass
class User:
    id: str | UUID
    username: str
    email: str

    @property
    def id(self) -> str:
        return str(self.id)
