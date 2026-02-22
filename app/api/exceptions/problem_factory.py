"""Фабрика для генерации DTO ошибок в формате RFC 7807."""

from enum import Enum

class ErrorCodes(Enum):
    """Перечисление стандартных кодов ошибок API.

    Каждый элемент содержит:

    - code (str): уникальный идентификатор типа ошибки.
    - title (str): краткое описание ошибки.
    - status (int): HTTP-статус, соответствующий ошибке.

    Используется для генерации стандартизированного словаря
    ошибки в формате `application/problem+json`.
    """

    SERVICE_CONNECTION_ERROR = (
        "service-connection-error",
        "Ошибка подключения к сервису",
        500,
    )

    VALIDATION_ERROR = (
        "validation-error",
        "Ошибка валидации данных",
        400,
    )

    AUTHENTICATION_ERROR = (
        "authentication-error",
        "Ошибка аутентификации",
        401,
    )

    AUTHORIZATION_ERROR = (
        "authorization-error",
        "Ошибка авторизации",
        403,
    )

    IMAGE_UPLOAD_ERROR = (
        "image-upload-error",
        "Ошибка загрузки изображения",
        400,
    )

    IMAGE_DELETION_ERROR = (
        "delete-image-error",
        "Ошибка удаления изображения",
        400,
    )

    TOO_MANY_REQUESTS_ERROR = (
        "too-many-requests-error",
        "Слишком много запросов",
        429,
    )

    def __init__(self, code: str, title: str, status: int) -> None:
        """Инициализация элемента перечисления.

        Args:
            code (str): Уникальный идентификатор типа ошибки.
            title (str): Краткое название ошибки.
            status (int): HTTP-статус, соответствующий ошибке.
        """
        self.code = code
        self.title = title
        self.status = status

    def example(self, detail: str) -> dict[str, str | int]:
        """Генерирует словарь ошибки в формате Problem Details.

        Args:
            detail (str): Детализированное сообщение об ошибке.

        Returns:
             dict[str, str | int]: Структура ошибки, совместимая с `application/problem+json`.
        """
        return {
            "type": f"https://example.com/probs/{self.code}",
            "title": self.title,
            "status": self.status,
            "detail": detail,
        }