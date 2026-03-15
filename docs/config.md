# Модуль config

Модуль содержит конфигурацию приложения.

Модуль загружает переменные окружения через dotenv и предоставляет
централизованное место для хранения всех настроек приложения, включая
базы данных, хранилища файлов, Redis, параметры токенов, правила
валидации данных, разрешённые расширения изображений и настройки
отладки.

## Класс Config

**Класс конфигурации приложения.**

Содержит параметры конфигурации, которые используются во всех слоях
приложения, включая доступ к базам данных, хранилищам файлов,
Redis, параметры токенов, правила валидации учетных данных,
разрешённые типы файлов для загрузки и настройки отладки.

```python
class Config:
    """Класс конфигурации приложения.

    Содержит параметры конфигурации, которые используются во всех слоях
    приложения, включая доступ к базам данных, хранилищам файлов,
    Redis, параметры токенов, правила валидации учетных данных,
    разрешённые типы файлов для загрузки и настройки отладки.
    """

    """Конфигурация баз данных"""
    # Конфигурация MongoDB
    DATABASE_HOST: str | None = os.getenv("DATABASE_HOST")
    DATABASE_PORT: int | None = os.getenv("DATABASE_PORT")
    DATABASE_USER: str | None = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD: str | None = os.getenv("DATABASE_PASSWORD")
    DATABASE_NAME: str | None = os.getenv("DATABASE_NAME")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"mongodb://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}",
    )

    # Конфигурация MinIO.
    MINIO_ENDPOINT: str | None = os.getenv("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str | None = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str | None = os.getenv("MINIO_SECRET_KEY")
    MINIO_BUCKET: str | None = os.getenv("MINIO_BUCKET")

    # Конфигурация Redis.
    REDIS_HOST: str | None = os.getenv("REDIS_HOST")
    REDIS_PORT: int | None = os.getenv("REDIS_PORT")
    REDIS_TOKENS_BLACKLIST_DB: int | None = os.getenv("REDIS_TOKENS_BLACKLIST_DB")
    REDIS_RATE_LIMITING_DB: int | None = os.getenv("REDIS_RATE_LIMITING_DB")
    REDIS_PASSWORD: str | None = os.getenv("REDIS_PASSWORD")

    """Конфигурация токенов."""
    TOKEN_SECRET_KEY: str | None = os.getenv("TOKEN_SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_TIME: int = 300
    REFRESH_TOKEN_EXPIRE_TIME: int = 1209600

    """Конфигурация валидации данных."""

    # Имя пользователя
    USERNAME_MIN_LENGTH: int = 3
    USERNAME_MAX_LENGTH: int = 255

    # Почта
    EMAIL_MAX_LENGTH: int = 255

    # Пароль
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_SPEC_SYMBOLS: frozenset[str] = frozenset(
        {
            "!",
            "@",
            "#",
            "$",
            "%",
            "^",
            "&",
            "*",
            "(",
            ")",
            "?",
            "|",
            "/",
            "<",
            ">",
            "_",
            "-",
        }
    )

    # Изображения
    ALLOWED_IMAGE_EXTENSIONS: tuple[str, ...] = (
        "jpg",
        "jpeg",
        "png",
    )

    """Конфигурация дебага"""
    DEBUG: str | None = os.getenv("DEBUG")

    """Конфигурация API запросов к LLM"""
    API_KEY: str | None = os.getenv("OPENAI_API_KEY")

    """Иная конфигурация"""
    # Базовый URL для фабрики ошибок: app/api/exceptions/problem_factory.py
    BASE_PROBLEM_URI = "https://example.com/probs"
```