# app/core/errors/problem.py
"""Фабрика DTO ошибок в формате RFC 7807 (application/problem+json)."""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.config import config as app_config, Config


@dataclass(slots=True, frozen=True)
class ErrorMeta:
    """Метаданные ошибки."""
    code: str
    title: str
    status: int

    def to_problem(self, detail: str, base_uri: str, **extra: Any) -> dict[str, Any]:
        """Преобразует в Problem Details dict."""
        result = {
            "type": f"{base_uri}/{self.code}",
            "title": self.title,
            "status": self.status,
            "detail": detail,
        }
        result.update(extra)
        return result


class ErrorCode(Enum):
    """Все коды ошибок приложения."""
    
    # Валидация (400)
    VALIDATION_ERROR = ErrorMeta("validation-error", "Ошибка валидации данных", 400)
    IMAGE_UPLOAD_ERROR = ErrorMeta("image-upload-error", "Ошибка загрузки изображения", 400)
    IMAGE_DELETION_ERROR = ErrorMeta("image-deletion-error", "Ошибка удаления изображения", 400)
    UNSUPPORTED_MEDIA_TYPE = ErrorMeta("unsupported-media-type", "Не поддерживаемый формат изображения", 415)
    
    # Аутентификация (401)
    AUTHENTICATION_ERROR = ErrorMeta("authentication-error", "Ошибка аутентификации", 401)
    
    # Авторизация (403)
    AUTHORIZATION_ERROR = ErrorMeta("authorization-error", "Ошибка авторизации", 403)
    
    # Конфликт (409)
    CONFLICT_ERROR = ErrorMeta("conflict-error", "Конфликт данных", 409)
    
    # Rate Limit (429)
    TOO_MANY_REQUESTS = ErrorMeta("too-many-requests", "Превышен лимит запросов", 429)
    
    # Серверные (500)
    SERVER_ERROR = ErrorMeta("server-error", "Ошибка сервера", 500)
    SERVICE_CONNECTION_ERROR = ErrorMeta("service-connection-error", "Ошибка подключения к сервису", 500)


class ProblemFactory:
    """Фабрика для создания Problem Details."""
    
    __slots__ = ("_base_uri",)
    
    def __init__(self, config: Config = app_config) -> None:
        self._base_uri = config.BASE_PROBLEM_URI
    
    def build(self, error: ErrorCode, detail: str, **extra: Any) -> dict[str, Any]:
        """Создаёт Problem Details dict.
        
        Args:
            error: Код ошибки из ErrorCode
            detail: Детальное описание ошибки
            **extra: Дополнительные поля (например, retry_after)
        
        Returns:
            Словарь в формате RFC 7807
        """
        return error.value.to_problem(detail, self._base_uri, **extra)
    
    def build_from_meta(self, meta: ErrorMeta, detail: str, **extra: Any) -> dict[str, Any]:
        """Создаёт Problem Details напрямую из ErrorMeta."""
        return meta.to_problem(detail, self._base_uri, **extra)


# Глобальный экземпляр для удобства
problem_factory = ProblemFactory()
