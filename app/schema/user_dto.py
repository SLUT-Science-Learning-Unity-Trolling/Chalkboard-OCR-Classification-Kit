from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field


class UserCreateDTO(BaseModel):
    username: str
    email: EmailStr
    password: str


class MongoUserDTO(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    username: str
    email: EmailStr
    password_hash: str


class UserDTO(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    username: str
    email: EmailStr
