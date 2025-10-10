"""Модуль содержит интерфейс DBGatewayInterface для работы с базой данных."""
# DBGatewayInterface

from abc import ABC, abstractmethod
from typing import Any


class DBGatewayInterface(ABC):
    """Гейтвей для подключения к базе данных."""

    @abstractmethod
    def get_connection(self, **kwargs: dict[str, Any]) -> Any:
        """Получение или создание коннекшена."""
        raise NotImplementedError
