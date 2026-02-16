"""Модуль содержит репозиторий для работы с Redis (например, для blacklist refresh токенов)."""
# RedisRepo

from app.adapters.gateways.redis import RedisGateway


class RedisRepo:
    """Репозиторий для работы с Redis."""
    
    def __init__(self, gateway: RedisGateway) -> None:
        """Инициализация репозитория.

        Args:
            gateway (RedisGateway): Гейтвей для подключения к Redis.
        """
        self._gateway = gateway

    async def add_to_blacklist(self, jti: str, expires_in: int) -> None:
        """Добавляет JTI токена в blacklist с указанием времени жизни.

        Args:
            jti (str): Идентификатор refresh токена.
            expires_in (int): Время жизни в секундах.
        """
        client = await self._gateway.get_connection()
        await client.set(f"blacklist:{jti}", "true", ex=expires_in)

    async def is_blacklisted(self, jti: str) -> bool:
        """Проверяет, находится ли JTI токена в blacklist.

        Args:
            jti (str): Идентификатор refresh токена.

        Returns:
            bool: True, если токен в blacklist, иначе False.
        """
        client = await self._gateway.get_connection()
        exists = await client.exists(f"blacklist:{jti}")
        return exists == 1

    async def remove_from_blacklist(self, jti: str) -> None:
        """Удаляет JTI токена из blacklist (опционально)."""
        client = await self._gateway.get_connection()
        await client.delete(f"blacklist:{jti}")
