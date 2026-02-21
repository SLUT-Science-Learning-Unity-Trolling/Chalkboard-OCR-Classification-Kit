## Класс ErrorCodes

**Коды ошибок для API.**

---
## def validation_error:
#### Ошибки валидации

```python
    @staticmethod
    def validation_error(detail: str) -> dict[str, str | int]:
        """Ошибки валидации"""
        return {
            "type": "https://example.com/probs/validation-error",
            "title": "Ошибка валидации данных",
            "status": 400,
            "detail": detail,
        }
```
---
## def conflict_error:
#### Ошибки конфликта данных

```python
    @staticmethod
    def conflict_error(detail: str) -> dict[str, str | int]:
        """Ошибки конфликта данных"""
        return {
            "type": "https://example.com/probs/conflict-error",
            "title": "Конфликт данных",
            "status": 409,
            "detail": detail,
        }
```
---
## def authentication_error:
#### Ошибки аутентификации

```python
    @staticmethod
    def authentication_error(detail: str) -> dict[str, str | int]:
        """Ошибки аутентификации"""
        return {
            "type": "https://example.com/probs/authentication-error",
            "title": "Ошибка аутентификации",
            "status": 401,
            "detail": detail,
        }
```
---
## def server_error:
#### Ошибки сервера

```python
    @staticmethod
    def server_error(detail: str) -> dict[str, str | int]:
        """Ошибки сервера"""
        return {
            "type": "https://example.com/probs/server-error",
            "title": "Ошибка сервера",
            "status": 500,
            "detail": detail,
        }
```
---
## def authorization_error:
#### Ошибки авторизации

```python
    @staticmethod
    def authorization_error(detail: str) -> dict[str, str | int]:
        """Ошибки авторизации"""
        return {
            "type": "https://example.com/probs/authorization-error",
            "title": "Ошибка авторизации",
            "status": 403,
            "detail": detail,
        }
```
---
## def too_many_requests_error:
#### Ошибки rate limit

```python
    @staticmethod
    def too_many_requests_error(detail: str) -> dict[str, str | int]:
        """Ошибки rate limit"""
        return {
            "type": "https://example.com/probs/too-many-requests-error",
            "title": "Превышен лимит запросов",
            "status": 429,
            "detail": detail,
        }
```
---
## def create_problem_response:
#### Фабрика RFC 7807 Problem Details response.

```python
def create_problem_response(body: dict[str, str | int]) -> Response:
    """Фабрика RFC 7807 Problem Details response."""
    return Response(
        content=body,
        status_code=body["status"],
        media_type="application/problem+json",
    )
```
---
## def handler_factory:
#### Фабрика хендлера.

```python
def handler_factory(problem_builder: Callable[[str], dict[str, str | int]]) -> Callable:
    """Фабрика хендлера."""
    def handler(request: Request, exc: Exception) -> Response:
        """Создаёт хендлер для ошибок."""
        detail: str = str(getattr(exc, "message", exc))
        return create_problem_response(problem_builder(detail))
    return handler
```
---
## def too_many_requests_handler:
#### Хендлер для rate-limit

```python
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
```
---