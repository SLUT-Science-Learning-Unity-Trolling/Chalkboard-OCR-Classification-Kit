"""Модуль содержит класс AuthService для аутентификации пользователей."""
# AuthService

import re
import secrets

from litestar import Request
from punq import Container

from app.adapters.repositories.abc_repo import RepositoryInterface
from app.adapters.repositories.redis_repo import RedisRepo
from app.api.schemas.user_dto import UserDTO
from app.config import config, token_key
from app.core.errors.auth import (
    InvalidEmailOrPasswordError,
    UnauthorizedError,
)
from app.core.services.security_service import SecurityService
from app.core.services.user_service import UserService
import paseto


class AuthService:
    """Сервис для аутентификации пользователей.

    Обрабатывает логин пользователей, проверку пароля и генерацию JWT-токенов.
    """

    def __init__(
        self,
        repository: RepositoryInterface,
        security: SecurityService,
        redis_repo: RedisRepo,
    ) -> None:
        """Инициализация сервиса аутентификации.

        Args:
            repository (RepositoryInterface): Репозиторий пользователей.
            security (SecurityService): Сервис для работы с хэшированием паролей.
        """
        self._repo = repository
        self._security = security
        self._redis = redis_repo
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
            raise InvalidEmailOrPasswordError

        hash, salt = self._security.deserialize_hash(user["password_hash"])
        if not self._security.verify_hash(password=password, salt=salt, hash_=hash):
            raise InvalidEmailOrPasswordError


        access_token = paseto.create(
            key=token_key,
            purpose="local",
            claims={
                "sub": str(user["_id"]),
                "username": user["username"],
                "email": user["email"],
                "type": "access",
                "jti": secrets.token_hex(8),
            },
            exp_seconds=config.ACCESS_TOKEN_EXPIRE_TIME,
        )


        refresh_token = paseto.create(
            key=token_key,
            purpose="local",
            claims={
                "sub": str(user["_id"]),
                "type": "refresh",
                "jti": secrets.token_hex(16),
            },
            exp_seconds=config.REFRESH_TOKEN_EXPIRE_TIME,
        )

        user_dto = UserDTO(
            id=str(user["_id"]),
            username=user["username"],
            email=user["email"],
        )

        return user_dto, access_token, refresh_token

    @staticmethod
    async def get_current_user(
        request: Request, container: Container
    ) -> UserDTO | None:
        """Возвращает текущего авторизованного пользователя.

        Проверяет JWT-токен в cookies запроса, извлекает пользователя из базы
        через UserService и возвращает его DTO.

        Args:
            request (Request): HTTP-запрос.
            container (Container): Контейнер зависимостей для получения сервисов.

        Returns:
            Optional[UserDTO]: DTO текущего пользователя или None, если пользователь не авторизован.
        """
        token = request.cookies.get("access_token")
        if not token:
            return None

        try:
            parsed = paseto.parse(
                key=token_key,
                purpose="local",
                token=token,
            )

            claims = parsed["message"]

            if claims.get("type") != "access":
                return None

            user_id = claims["sub"]

        except Exception:
            return None

        user_service = container.resolve(UserService)
        user = await user_service.get_user_by_id(user_id)

        if not user:
            return None

        return UserDTO.fromrow(user)
    

    async def refresh_tokens(self, refresh_token: str, access_token: str | None) -> tuple[str, str]:
        """Перевыпуск access и refresh токена по валидному refresh_token."""

        if not refresh_token:
            raise UnauthorizedError("Refresh token is required")

        def _parse_paseto(token: str, expected_type: str) -> dict:
            """Парсинг PASETO и проверка типа токена."""
            try:
                parsed = paseto.parse(key=token_key, purpose="local", token=token)
                claims = parsed["message"]
            except Exception:
                raise UnauthorizedError(f"Invalid {expected_type} token")

            if claims.get("type") != expected_type:
                raise UnauthorizedError(f"Token is not of type {expected_type}")

            jti = claims.get("jti")
            if not jti:
                raise UnauthorizedError(f"{expected_type.capitalize()} token missing jti")

            return claims

        claims_refresh = _parse_paseto(refresh_token, "refresh")
        refresh_jti = claims_refresh["jti"]

        if self._redis and await self._redis.is_blacklisted(refresh_jti):
            raise UnauthorizedError("Refresh token is blacklisted")

        user_id = claims_refresh["sub"]

        claims_access = None
        access_jti = None
        if access_token:
            claims_access = _parse_paseto(access_token, "access")
            access_jti = claims_access["jti"]
            if self._redis and await self._redis.is_blacklisted(access_jti):
                raise UnauthorizedError("Access token is blacklisted")

        new_access = paseto.create(
            key=token_key,
            purpose="local",
            claims={
                "sub": user_id,
                "type": "access",
                "jti": secrets.token_hex(8),
            },
            exp_seconds=config.ACCESS_TOKEN_EXPIRE_TIME,
        )

        new_refresh = paseto.create(
            key=token_key,
            purpose="local",
            claims={
                "sub": user_id,
                "type": "refresh",
                "jti": secrets.token_hex(16),
            },
            exp_seconds=config.REFRESH_TOKEN_EXPIRE_TIME,
        )

        if self._redis:
            await self._redis.add_to_blacklist(refresh_jti, expires_in=config.REFRESH_TOKEN_EXPIRE_TIME)
            if access_jti:
                await self._redis.add_to_blacklist(access_jti, expires_in=config.ACCESS_TOKEN_EXPIRE_TIME)

        return new_access, new_refresh