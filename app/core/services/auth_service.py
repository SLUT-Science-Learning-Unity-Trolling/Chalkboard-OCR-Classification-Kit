from typing import Optional
from punq import Container


from litestar import Request
from app.core.services.security_service import SecurityService
from app.core.services.user_service import UserService
from app.core.errors.auth import InvalidEmailOrPassword
from app.adapters.repositories.__abc_repo__ import RepositoryInterface
from app.jam import jam
from app.config import config
from app.api.schemas.user_dto import UserDTO


class AuthService:
    """Сервис для аутентификации пользователей."""

    def __init__(
        self,
        repository: RepositoryInterface,
        security: SecurityService,
    ):
        """Конструктор.

        Args:
            repository (RepositoryInterface): Репозиторий
            security (SecurityService): Секьюрити сервис
        """
        self._repo = repository
        self._security = security
        pass

    async def auth_existing_user(
        self, email: str, password: str
    ) -> tuple[UserDTO, str]:
        """Аутентификация существующего пользователя."""
        user = await self._repo.get_one({"email": email.lower()})
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
        """Возвращает текущего пользователя или None, если не авторизован."""
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
