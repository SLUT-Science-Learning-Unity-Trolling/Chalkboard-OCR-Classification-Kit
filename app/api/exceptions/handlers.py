# app/core/errors/handlers.py
"""Обработчики исключений для Litestar."""

from typing import Callable, Type, Any

from litestar import Request, Response

from app.api.exceptions.problem_factory import ErrorCode, ProblemFactory, problem_factory
from app.core.errors.auth import (
    PasswordDontMatchError,
    EmailValidationError,
    EmailAlreadyTakenError,
    UsernameAlreadyTakenError,
    InvalidEmailOrPasswordError,
    UnauthorizedError,
)
from app.core.errors.security import TooManyRequestsError
from app.core.errors.user import (
    AbsentUserError, 
    DeleteImageError, 
    GetImagesError, 
    ImageUploadError, 
    UserCreationError,
)
from app.core.errors.validation import (
    ImageExtensionValidationError,
    ImageValidationError,
    PasswordValidationError,
    UsernameValidationError,
    IdentificatorIsNullError,
)


def create_problem_response(
    body: dict[str, Any], 
    headers: dict[str, str] | None = None
) -> Response:
    """Создаёт HTTP-ответ в формате RFC 7807."""
    return Response(
        content=body,
        status_code=body["status"],
        media_type="application/problem+json",
        headers=headers,
    )


def create_handler(
    error_code: ErrorCode,
    factory: ProblemFactory = problem_factory,
) -> Callable[[Request, Exception], Response]:
    """Создаёт обработчик для указанного типа ошибки."""
    
    def handler(request: Request, exc: Exception) -> Response:
        detail = str(getattr(exc, "message", str(exc)))
        body = factory.build(error_code, detail)
        return create_problem_response(body)
    
    return handler


def too_many_requests_handler(
    request: Request, 
    exc: TooManyRequestsError,
) -> Response:
    """Специальный обработчик для rate limit с Retry-After."""
    detail = str(getattr(exc, "message", str(exc)))
    
    extra = {}
    headers = {}
    
    if exc.retry_after is not None:
        headers["Retry-After"] = str(exc.retry_after)
        extra["retry_after"] = exc.retry_after
    
    body = problem_factory.build(ErrorCode.TOO_MANY_REQUESTS, detail, **extra)
    return create_problem_response(body, headers)


# Маппинг исключений на коды ошибок
ERROR_MAPPING: dict[ErrorCode, tuple[type[Exception], ...]] = {
    ErrorCode.VALIDATION_ERROR: (
        PasswordDontMatchError,
        PasswordValidationError,
        UsernameValidationError,
        EmailValidationError,
        IdentificatorIsNullError,
    ),
    ErrorCode.CONFLICT_ERROR: (
        EmailAlreadyTakenError,
        UsernameAlreadyTakenError,
    ),
    ErrorCode.AUTHENTICATION_ERROR: (
        InvalidEmailOrPasswordError,
        UnauthorizedError,
    ),
    ErrorCode.AUTHORIZATION_ERROR: (
        ImageUploadError,
        AbsentUserError,
    ),
    ErrorCode.SERVER_ERROR: (
        UserCreationError,
        GetImagesError,
        DeleteImageError,
    ),
    ErrorCode.UNSUPPORTED_MEDIA_TYPE: (
        ImageExtensionValidationError,
        ImageValidationError
        
    )
}


def build_exception_handlers() -> dict[Type[Exception], Callable]:
    """Строит словарь обработчиков исключений."""
    handlers: dict[Type[Exception], Callable] = {}
    
    for error_code, exceptions in ERROR_MAPPING.items():
        handler = create_handler(error_code)
        for exc_type in exceptions:
            handlers[exc_type] = handler
    
    handlers[TooManyRequestsError] = too_many_requests_handler
    
    return handlers


EXCEPTION_HANDLERS = build_exception_handlers()
