# -*- coding: utf-8 -*-
# AuthService

from typing import Optional
from punq import Container
import re

from litestar import Request
from app.core.services.security_service import SecurityService
from app.core.services.user_service import UserService
from app.core.errors.auth import InvalidEmailOrPassword
from app.adapters.repositories.abc_repo import RepositoryInterface
from app.config import jam
from app.config import config
from app.api.schemas.user_dto import UserDTO


class AuthService:
    """Сервис для аутентификации пользователей.

    Обрабатывает логин пользователей, проверку пароля и генерацию JWT-токенов.
    """

    def __init__(
        self,
        repository: RepositoryInterface,
        security: SecurityService,
    ) -> None:
        """Инициализация сервиса аутентификации.

        Args:
            repository (RepositoryInterface): Репозиторий пользователей.
            security (SecurityService): Сервис для работы с хэшированием паролей.
        """
        self._repo = repository
        self._security = security
        pass

    async def auth_existing_user(
        self, identifier: str, password: str
    ) -> tuple[UserDTO, str]:
        """Аутентификация существующего пользователя по email или username.

        Проверяет существование пользователя, валидирует пароль и
        генерирует JWT-токен для авторизации.

        Args:
            identifier (str): Email или имя пользователя (username).
            password (str): Пароль пользователя.

        Raises:
            InvalidEmailOrPassword: Если пользователь не найден или пароль неверный.

        Returns:
            tuple[UserDTO, str]: DTO пользователя и JWT-токен.
        """
        if re.match(r"[^@]+@[^@]+\.[^@]+", identifier):
            query = {"email": identifier.lower()}
        else:
            query = {"username": identifier}

        user = await self._repo.get_one(query)
        if not user:
            raise InvalidEmailOrPassword

        hash, salt = self._security.deserialize_hash(user["password_hash"])
        if not self._security.verify_hash(
            password=password, salt=salt, hash_=hash
        ):
            raise InvalidEmailOrPassword

        payload = jam.make_payload(
            exp=config.JWT_EXPIRE_TIME,
            data={
                "user_id": str(user["_id"]),
                "email": user["email"],
                "username": user["username"],
            },
        )

        token = jam.gen_jwt_token(payload)

        user_dto = UserDTO(
            id=str(user["_id"]),
            username=user["username"],
            email=user["email"],
        )

        return user_dto, token

    @staticmethod
    async def get_current_user(
        request: Request, container: Container
    ) -> Optional[UserDTO]:
        """Возвращает текущего авторизованного пользователя.

        Проверяет JWT-токен в cookies запроса, извлекает пользователя из базы
        через UserService и возвращает его DTO.

        Args:
            request (Request): HTTP-запрос.
            container (Container): Контейнер зависимостей для получения сервисов.

        Returns:
            Optional[UserDTO]: DTO текущего пользователя или None, если пользователь не авторизован.
        """
        token = request.cookies.get("token")
        if not token:
            return None

        try:
            payload = jam.verify_jwt_token(
                token=token, check_exp=True, check_list=False
            )
            user_id = payload["data"]["user_id"]
        except Exception:
            return None

        user_service = container.resolve(UserService)
        user = await user_service.get_user_by_id(user_id)
        if not user:
            return None

        return UserDTO.fromrow(user)
