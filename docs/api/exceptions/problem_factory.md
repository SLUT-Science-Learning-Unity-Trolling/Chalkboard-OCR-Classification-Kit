# Модуль problem_factory

Фабрика DTO ошибок в формате RFC 7807 (application/problem+json).

## Класс ErrorMeta

**Метаданные ошибки.**

```python
@dataclass(slots=True, frozen=True)
class ErrorMeta:
    """Метаданные ошибки."""
    code: str
    title: str
    status: int
```

---
## def to_problem:
#### Преобразует в Problem Details dict.

```python
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
```
---
## Класс ErrorCode

**Все коды ошибок приложения.**

```python
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
```
## Класс ProblemFactory

**Фабрика для создания Problem Details.**

```python
class ProblemFactory:
    """Фабрика для создания Problem Details."""
    
    __slots__ = ("_base_uri",)
```

---
## def init:

```python
    def __init__(self, config: Config = app_config) -> None:
        self._base_uri = config.BASE_PROBLEM_URI
```
---
## def build:
#### Создаёт Problem Details dict.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `error` | `` | Код ошибки из ErrorCode |
| `detail` | `` | Детальное описание ошибки |
| `**extra` | `` | Дополнительные поля (например, retry_after) |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `Словарь в формате RFC 7807` | |

```python
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
```
---
## def build_from_meta:
#### Создаёт Problem Details напрямую из ErrorMeta.

```python
    def build_from_meta(self, meta: ErrorMeta, detail: str, **extra: Any) -> dict[str, Any]:
        """Создаёт Problem Details напрямую из ErrorMeta."""
        return meta.to_problem(detail, self._base_uri, **extra)
```
---