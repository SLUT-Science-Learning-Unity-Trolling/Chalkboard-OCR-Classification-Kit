## Класс ErrorCodes

**Фабрика тел ошибок в формате RFC 7807 (Problem Details for HTTP APIs).**

Предоставляет статические методы для генерации стандартизированных
структур ошибок API, соответствующих media-type:
`application/problem+json`.

Каждая структура содержит:

- type: URI-идентификатор типа ошибки
- title: краткое описание
- status: HTTP-статус
- detail: детализированное сообщение

```python
class ErrorCodes:
    """Фабрика тел ошибок в формате RFC 7807 (Problem Details for HTTP APIs).

    Предоставляет статические методы для генерации стандартизированных
    структур ошибок API, соответствующих media-type:
    `application/problem+json`.

    Каждая структура содержит:

    - type: URI-идентификатор типа ошибки
    - title: краткое описание
    - status: HTTP-статус
    - detail: детализированное сообщение

    """
```

---
## def validation_error:
#### Ошибки валидаци.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `detail` | `str` | Детали ошибки |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `dicts (dict[str, str | int])` | RFC 7807-совместимая структура ошибки. |

```python
    @staticmethod
    def validation_error(detail: str) -> dict[str, str | int]:
        """Ошибки валидаци.
        
        Args:
            detail (str): Детали ошибки
        Returns:
            dicts (dict[str, str | int]): RFC 7807-совместимая структура ошибки.
        """
        return {
            "type": "https://example.com/probs/validation-error",
            "title": "Ошибка валидации данных",
            "status": 400,
            "detail": detail,
        }
```
---
## def conflict_error:
#### Ошибки конфликта данных.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `detail` | `str` | Детали ошибки |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `dicts (dict[str, str | int])` | RFC 7807-совместимая структура ошибки. |

```python
    @staticmethod
    def conflict_error(detail: str) -> dict[str, str | int]:
        """Ошибки конфликта данных.
        
        Args:
            detail (str): Детали ошибки
        Returns:
            dicts (dict[str, str | int]): RFC 7807-совместимая структура ошибки.
        """
        return {
            "type": "https://example.com/probs/conflict-error",
            "title": "Конфликт данных",
            "status": 409,
            "detail": detail,
        }
```
---
## def authentication_error:
#### Ошибки аутентификации.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `detail` | `str` | Детали ошибки |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `dicts (dict[str, str | int])` | RFC 7807-совместимая структура ошибки. |

```python
    @staticmethod
    def authentication_error(detail: str) -> dict[str, str | int]:
        """Ошибки аутентификации.
        
        Args:
            detail (str): Детали ошибки
        Returns:
            dicts (dict[str, str | int]): RFC 7807-совместимая структура ошибки.
        """
        return {
            "type": "https://example.com/probs/authentication-error",
            "title": "Ошибка аутентификации",
            "status": 401,
            "detail": detail,
        }
```
---
## def server_error:
#### Ошибки сервера.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `detail` | `str` | Детали ошибки |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `dicts (dict[str, str | int])` | RFC 7807-совместимая структура ошибки. |

```python
    @staticmethod
    def server_error(detail: str) -> dict[str, str | int]:
        """Ошибки сервера.
        
        Args:
            detail (str): Детали ошибки
        Returns:
            dicts (dict[str, str | int]): RFC 7807-совместимая структура ошибки.
        """
        return {
            "type": "https://example.com/probs/server-error",
            "title": "Ошибка сервера",
            "status": 500,
            "detail": detail,
        }
```
---
## def authorization_error:
#### Ошибки авторизации.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `detail` | `str` | Детали ошибки |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `dicts (dict[str, str | int])` | RFC 7807-совместимая структура ошибки. |

```python
    @staticmethod
    def authorization_error(detail: str) -> dict[str, str | int]:
        """Ошибки авторизации.
        
        Args:
            detail (str): Детали ошибки
        Returns:
            dicts (dict[str, str | int]): RFC 7807-совместимая структура ошибки.
        """
        return {
            "type": "https://example.com/probs/authorization-error",
            "title": "Ошибка авторизации",
            "status": 403,
            "detail": detail,
        }
```
---
## def too_many_requests_error:
#### Ошибки rate limit.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `detail` | `str` | Детали ошибки |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `dicts (dict[str, str | int])` | Ошибка по RFC 7807 |

```python
    @staticmethod
    def too_many_requests_error(detail: str) -> dict[str, str | int]:
        """Ошибки rate limit.
        
        Args:
            detail (str): Детали ошибки
        Returns:
            dicts (dict[str, str | int]): Ошибка по RFC 7807
        """
        return {
            "type": "https://example.com/probs/too-many-requests-error",
            "title": "Превышен лимит запросов",
            "status": 429,
            "detail": detail,
        }
```
---
## def create_problem_response:
#### Создаёт HTTP-ответ в формате RFC 7807.

Формирует Response с media-type `application/problem+json`
и статус-кодом, соответствующим полю `status` в теле ошибки.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `body` | `` | Словарь с описанием ошибки (Problem Details). |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `Response` | объект готовый к возврату из обработчика Litestar. |

```python
def create_problem_response(body: dict[str, str | int]) -> Response:
    """Создаёт HTTP-ответ в формате RFC 7807.
    Формирует Response с media-type `application/problem+json`
    и статус-кодом, соответствующим полю `status` в теле ошибки.

    Args:
        body: Словарь с описанием ошибки (Problem Details).

    Returns:
        Response: объект готовый к возврату из обработчика Litestar.
    """
    return Response(
        content=body,
        status_code=body["status"],
        media_type="application/problem+json",
    )
```
---
## def handler_factory:
#### Фабрика универсальных exception handler'ов.

Создаёт функцию-обработчик, преобразующую исключение
в RFC 7807 Problem Details response.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `problem_builder` | `Callable[[str], dict[str, str \| int]]` | Функция, формирующая тело ошибки на основе строки detail. |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `Callable` | обработчик, совместимый с Litestar. |

```python
def handler_factory(problem_builder: Callable[[str], dict[str, str | int]]) -> Callable:
    """Фабрика универсальных exception handler'ов.

    Создаёт функцию-обработчик, преобразующую исключение
    в RFC 7807 Problem Details response.

    Args:
        problem_builder (Callable[[str], dict[str, str | int]]): Функция, формирующая тело ошибки на основе строки detail.

    Returns:
        Callable: обработчик, совместимый с Litestar.
    """
    def handler(request: Request, exc: Exception) -> Response:
        """Обрабатывает исключение и возвращает стандартизированный ответ.

        Args:
            request: Текущий HTTP-запрос.
            exc: Перехваченное исключение.

        Returns:
            Response: ответ в формате Problem Details.
        """
        detail: str = str(getattr(exc, "message", exc))
        return create_problem_response(problem_builder(detail))
    return handler
```
---
## def too_many_requests_handler:
#### Обработчик исключения превышения лимита запросов (HTTP 429).

Дополнительно устанавливает заголовок `Retry-After`,
если значение присутствует в исключении.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `request` | `` | Текущий HTTP-запрос. |
| `exc` | `` | Исключение TooManyRequestsError. |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `Response` | ответ с телом RFC 7807 и при необходимости заголовком Retry-After. |

```python
def too_many_requests_handler(request: Request, exc: TooManyRequestsError) -> Response:
    """Обработчик исключения превышения лимита запросов (HTTP 429).

    Дополнительно устанавливает заголовок `Retry-After`,
    если значение присутствует в исключении.

    Args:
        request: Текущий HTTP-запрос.
        exc: Исключение TooManyRequestsError.

    Returns:
        Response: ответ с телом RFC 7807 и при необходимости заголовком Retry-After.
    """
    ...
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