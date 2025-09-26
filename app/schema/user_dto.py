from uuid import UUID

from pydantic import BaseModel


class UserDTO(BaseModel):
    id: str | UUID
    username: str
    email: str
