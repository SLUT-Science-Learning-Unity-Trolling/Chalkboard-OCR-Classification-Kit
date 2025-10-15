"""Модуль содержит конфигурацию приложения."""
# Config

import os

from dotenv import load_dotenv
from jam import Jam


load_dotenv()


class Config:
    """Класс конфигурации приложения."""

    """Кофигурация базы данных."""
    DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT = os.getenv("DATABASE_PORT", "27017")
    DATABASE_USER = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "mongodb")
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"mongodb://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}",
    )

    """Конфигурация JWT."""
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_EXPIRE_TIME = 1209600

    """Конфигурация валидации данных."""
    USERNAME_MIN_LENGTH = 3
    USERNAME_MAX_LENGTH = 50
    EMAIL_MAX_LENGTH = 255
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_SPEC_SYMBOLS = [
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
    ]
    ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "tif", "tiff"]

    """Конфигурация MinIO."""
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
    MINIO_BUCKET = os.getenv("MINIO_BUCKET")

    """Прочая конфигурация."""
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"


config: Config = Config()


"""Конфиг Jam для аутентификации."""
jam_config = {
    "auth_type": "jwt",
    "secret_key": config.JWT_SECRET_KEY,
    "alg": "HS256",
    "expire": config.JWT_EXPIRE_TIME,
}

jam = Jam(config=jam_config)
