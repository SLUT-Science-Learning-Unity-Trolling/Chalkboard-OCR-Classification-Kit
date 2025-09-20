from abc import ABC, abstractmethod
from typing import List


class AbstractRepo(ABC):
    """
    Абстрактный класс для наследования новых
    репозиториев

    Info:
        Новые методы по мере разрабтки

    Raises:
        (NotImplementedError) - Для того, чтобы никто не мог использовать интерфейс как репозиторий
    """

    @abstractmethod
    async def find_one(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self) -> List:
        raise NotImplementedError

    @abstractmethod
    async def create_some(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_or_create(self, **kwargs):
        raise NotImplementedError
