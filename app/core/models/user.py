from dataclasses import dataclass

from bson import ObjectId


@dataclass
class User:
    _id: ObjectId
    username: str
    email: str

    @property
    def id(self) -> str:
        return str(self._id)
