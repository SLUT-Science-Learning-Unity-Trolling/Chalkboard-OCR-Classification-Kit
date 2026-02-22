"""Модуль содержит конфигурацию приложения и ключи для PASETO токенов.

Модуль загружает переменные окружения через dotenv и предоставляет
централизованное место для хранения всех настроек приложения, включая
базы данных, хранилища файлов, Redis, параметры токенов, правила
валидации данных, разрешённые расширения изображений и настройки
отладки.
"""
# Config

import os

from typing import Final

from dotenv import load_dotenv
from paseto.keys.symmetric_key import SymmetricKey
from paseto.protocols.v4 import ProtocolVersion4


load_dotenv()

class Config:
    """Класс конфигурации приложения.
    
    Содержит параметры конфигурации, которые используются во всех слоях
    приложения, включая доступ к базам данных, хранилищам файлов,
    Redis, параметры токенов, правила валидации учетных данных,
    разрешённые типы файлов для загрузки и настройки отладки.
    """

    """Конфигурация баз данных"""
    # Конфигурация MongoDB
    DATABASE_HOST: Final[str] = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: Final[int] = int(os.getenv("DATABASE_PORT", "27017"))
    DATABASE_USER: Final[str] = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD: Final[str] = os.getenv("DATABASE_PASSWORD")
    DATABASE_NAME: Final[str] = os.getenv("DATABASE_NAME", "mongodb")
    DATABASE_URL: Final[str] = os.getenv(
        "DATABASE_URL",
        f"mongodb://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}",
    )

    # Конфигурация MinIO.
    MINIO_ENDPOINT: Final[str] = os.getenv("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: Final[str] = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: Final[str] = os.getenv("MINIO_SECRET_KEY")
    MINIO_BUCKET: Final[str] = os.getenv("MINIO_BUCKET")

    # Конфигурация Redis.
    REDIS_HOST: Final[str] = os.getenv("REDIS_HOST")
    REDIS_PORT: Final[int] = int(os.getenv("REDIS_PORT"))
    REDIS_TOKENS_BLACKLIST_DB: Final[int] = int(os.getenv("REDIS_TOKENS_BLACKLIST_DB"))
    REDIS_RATE_LIMITING_DB: Final[int] = int(os.getenv("REDIS_RATE_LIMITING_DB"))
    REDIS_PASSWORD: Final[str] = os.getenv("REDIS_PASSWORD")

    """Конфигурация токенов."""
    TOKEN_SECRET_KEY: Final[str] = str(os.getenv("TOKEN_SECRET_KEY"))
    ACCESS_TOKEN_EXPIRE_TIME: Final[int] = 300
    REFRESH_TOKEN_EXPIRE_TIME: Final[int] = 1209600

    """Конфигурация валидации данных."""

    # Имя пользователя
    USERNAME_MIN_LENGTH: Final[int] = 3
    USERNAME_MAX_LENGTH: Final[int] = 255

    # Почта
    EMAIL_MAX_LENGTH: Final[int] = 255

    # Пароль
    PASSWORD_MIN_LENGTH: Final[int] = 8
    PASSWORD_SPEC_SYMBOLS: Final[frozenset[str]] = {"!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "?", "|", "/", "<", ">", "_", "-"}

    # Изображения
    ALLOWED_IMAGE_EXTENSIONS: Final[tuple[str, ...]] = ("jpg", "jpeg", "png", "tif", "tiff")

    """Конфигурация дебага"""
    DEBUG: Final[bool] = os.getenv("DEBUG")

    """Конфигурация API запросов к LLM"""
    API_KEY: Final[str] = os.getenv("OPENAI_API_KEY")


config: Config = Config()

token_key = SymmetricKey(config.TOKEN_SECRET_KEY.encode(), ProtocolVersion4)
