"""Модуль содержит конфигурацию приложения."""
# Config

import os

from pathlib import Path

from dotenv import load_dotenv
from jam import Jam


load_dotenv()


class Config:
    """Класс конфигурации приложения."""

    DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT = os.getenv("DATABASE_PORT", "27017")
    DATABASE_USER = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "mongodb")
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"mongodb://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}",
    )

    DEBUG: bool = os.getenv("DEBUG", "True") == "True"

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_EXPIRE_TIME = 1209600

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

    PROJECT_DIRS = [
        Path("app"),
        Path("tests"),
    ]
    DOCS_DIR = Path("docs")
    SUPPORTED_EXT = [".py"]
    WIKI_REPO = "https://github.com/SLUT-Science-Learning-Unity-Trolling/Chalkboard-OCR-Classification-Kit.wiki.git"
    LOCAL_WIKI_DIR = Path(".wiki_tmp")


config: Config = Config()


"""Конфиг Jam для аутентификации."""
jam_config = {
    "auth_type": "jwt",
    "secret_key": config.JWT_SECRET_KEY,
    "alg": "HS256",
    "expire": config.JWT_EXPIRE_TIME,
}

jam = Jam(config=jam_config)
