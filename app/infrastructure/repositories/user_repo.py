# -*- coding: utf-8 -*-

from app.core.models.user import User
from app.infrastructure.gateways.mongo import MongoGateway
from app.infrastructure.repositories.mongo_repo import MongoRepo
from app.schema.user_dto import UserDTO


class UserRepo(MongoRepo[User, UserDTO]):
    def __init__(self, gateway: MongoGateway):
        super().__init__(
            gateway=gateway,
            collection_name="users",
            dto_model=UserDTO,
            to_domain=User,
        )
