from uuid import uuid4

from pydantic import BaseModel, Field


class UserDTO(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    username: str
    email: str
