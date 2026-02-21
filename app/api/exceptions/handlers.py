# exceptions/handlers.py
from typing import Callable, Type
from litestar import Request, Response

from app.core.errors.auth import (
    PasswordDontMatchError,
    EmailValidationError,
    EmailAlreadyTakenError,
    UsernameAlreadyTakenError,
    InvalidEmailOrPasswordError,
    UnauthorizedError,
)
from app.core.errors.security import TooManyRequestsError
from app.core.errors.user import AbsentUserError, DeleteImageError, GetImagesError, ImageUploadError, UserCreationError
from app.core.errors.validation import (
    ImageExtensionValidationError,
    PasswordValidationError,
    UsernameValidationError,
    IdentificatorIsNullError,
)


class ErrorCodes:
    """Коды ошибок для API."""
    
    @staticmethod
    def validation_error(detail: str) -> dict[str, str | int]:
        """Ошибки валидации"""
        return {
            "type": "https://example.com/probs/validation-error",
            "title": "Ошибка валидации данных",
            "status": 400,
            "detail": detail,
        }
    
    @staticmethod
    def conflict_error(detail: str) -> dict[str, str | int]:
        """Ошибки конфликта данных"""
        return {
            "type": "https://example.com/probs/conflict-error",
            "title": "Конфликт данных",
            "status": 409,
            "detail": detail,
        }
    
    @staticmethod
    def authentication_error(detail: str) -> dict[str, str | int]:
        """Ошибки аутентификации"""
        return {
            "type": "https://example.com/probs/authentication-error",
            "title": "Ошибка аутентификации",
            "status": 401,
            "detail": detail,
        }
    
    @staticmethod
    def server_error(detail: str) -> dict[str, str | int]:
        """Ошибки сервера"""
        return {
            "type": "https://example.com/probs/server-error",
            "title": "Ошибка сервера",
            "status": 500,
            "detail": detail,
        }


    @staticmethod
    def authorization_error(detail: str) -> dict[str, str | int]:
        """Ошибки авторизации"""
        return {
            "type": "https://example.com/probs/authorization-error",
            "title": "Ошибка авторизации",
            "status": 403,
            "detail": detail,
        }

    @staticmethod
    def too_many_requests_error(detail: str) -> dict[str, str | int]:
        """Ошибки rate limit"""
        return {
            "type": "https://example.com/probs/too-many-requests-error",
            "title": "Превышен лимит запросов",
            "status": 429,
            "detail": detail,
        }

def create_problem_response(body: dict[str, str | int]) -> Response:
    """Фабрика RFC 7807 Problem Details response."""
    return Response(
        content=body,
        status_code=body["status"],
        media_type="application/problem+json",
    )


def handler_factory(problem_builder: Callable[[str], dict[str, str | int]]) -> Callable:
    """Фабрика хендлера."""
    def handler(request: Request, exc: Exception) -> Response:
        """Создаёт хендлер для ошибок."""
        detail: str = str(getattr(exc, "message", exc))
        return create_problem_response(problem_builder(detail))
    return handler

def too_many_requests_handler(request: Request, exc: TooManyRequestsError) -> Response:
    """Хендлер для rate-limit"""
    detail = str(getattr(exc, "message", exc))
    body = ErrorCodes.too_many_requests_error(detail)

    headers = {}
    if exc.retry_after is not None:
        headers["Retry-After"] = str(exc.retry_after)
        body["retry_after"] = exc.retry_after

    return Response(
        content=body,
        status_code=body["status"],
        media_type="application/problem+json",
        headers=headers,
    )

validation_errors: tuple[type[Exception], ...] = [
    PasswordDontMatchError,
    PasswordValidationError,
    UsernameValidationError,
    EmailValidationError,
    IdentificatorIsNullError,
]

conflict_errors: tuple[type[Exception], ...] = [
    EmailAlreadyTakenError,
    UsernameAlreadyTakenError,
]

auth_errors: tuple[type[Exception], ...] = [
    InvalidEmailOrPasswordError,
    UnauthorizedError,
]

authorization_errors: tuple[type[Exception], ...] = [
    ImageUploadError,
    AbsentUserError,
]

server_errors: tuple[type[Exception], ...] = [
    UserCreationError,
    GetImagesError,
    DeleteImageError,
    ImageExtensionValidationError,
]

EXCEPTION_HANDLERS: dict[Type[Exception], Callable] = {}
EXCEPTION_HANDLERS.update({exc: handler_factory(ErrorCodes.validation_error) for exc in validation_errors})
EXCEPTION_HANDLERS.update({exc: handler_factory(ErrorCodes.conflict_error) for exc in conflict_errors})
EXCEPTION_HANDLERS.update({exc: handler_factory(ErrorCodes.authentication_error) for exc in auth_errors})
EXCEPTION_HANDLERS.update({exc: handler_factory(ErrorCodes.authorization_error) for exc in authorization_errors})
EXCEPTION_HANDLERS.update({exc: handler_factory(ErrorCodes.server_error) for exc in server_errors})
EXCEPTION_HANDLERS.update({TooManyRequestsError: too_many_requests_handler})