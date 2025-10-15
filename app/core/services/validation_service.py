"""Модуль содержит класс ValidationService для валидации данных."""
# ValidationService

import os
import re

from litestar.datastructures import UploadFile

from app import config
from app.core.errors.validation import (
    PasswordValidationError,
    UsernameValidationError,
)


class ValidationService:
    """Сервис валидации."""

    def __init__(self, config: type[config.Config] = config.Config) -> None:
        """Инциализация.

        Args:
            config (Config): Конфиг
        """
        self.config = config

    async def validate_password(self, password: str) -> bool:
        """Валидатор паролей, настройки берутся из конфига.

        Args:
            password (str): Пароль для валидации

        Raises:
            PasswordValidationError: Ошибка при валидации пароля

        Returns:
            bool: True, если пароль валиден
        """
        if len(password) < self.config.PASSWORD_MIN_LENGTH:
            raise PasswordValidationError(
                f"Пароль должен быть минимум {self.config.PASSWORD_MIN_LENGTH} символов."
            )

        if not any(char.isdigit() for char in password):
            raise PasswordValidationError("Пароль должен содержать хотя бы одну цифру.")

        if not any(char.isupper() for char in password):
            raise PasswordValidationError(
                "Пароль должен содержать хотя бы одну заглавную букву."
            )

        if not any(char.islower() for char in password):
            raise PasswordValidationError(
                "Пароль должен содержать хотя бы одну строчную букву."
            )

        if not any(char in self.config.PASSWORD_SPEC_SYMBOLS for char in password):
            raise PasswordValidationError(
                f"Пароль должен содержать хотя бы один спец. символ из {self.config.PASSWORD_SPEC_SYMBOLS}."
            )

        return True

    async def validate_username(self, username: str) -> bool:
        """Проверка имени пользователя.

        Требования:
        - Минимальная длина: self.config.USERNAME_MIN_LENGTH
        - Максимальная длина: self.config.USERNAME_MAX_LENGTH
        - Разрешены только латинские буквы, цифры, символы _ и -

        Args:
            username (str): Имя пользователя

        Returns:
            bool: True, если имя пользователя валидно

        Raises:
            UsernameValidationError: Ошибка при валидации имени
        """
        if len(username) < self.config.USERNAME_MIN_LENGTH:
            raise UsernameValidationError(
                f"Имя пользователя должно быть не короче {self.config.USERNAME_MIN_LENGTH} символов."
            )

        if len(username) > self.config.USERNAME_MAX_LENGTH:
            raise UsernameValidationError(
                f"Имя пользователя не должно превышать {self.config.USERNAME_MAX_LENGTH} символов."
            )

        if not re.match(r"^[A-Za-z0-9_-]+$", username):
            raise UsernameValidationError(
                "Имя пользователя может содержать только латинские буквы, цифры, символы '_' и '-'."
            )

        return True

    async def validate_image_extension(self, file: UploadFile) -> bool:
        """Проверка расширения файла.

        Args:
            file (str | UploadFile): Имя файла или объект UploadFile

        Returns:
            bool: True, если расширение файла валидно
        """
        filename = file.filename

        _, ext = os.path.splitext(filename)
        ext = ext.lower().lstrip(".")

        return ext in self.config.ALLOWED_IMAGE_EXTENSIONS
