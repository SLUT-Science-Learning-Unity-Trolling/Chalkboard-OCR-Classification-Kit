from __future__ import annotations
import io

import pytest

from app.core.services.validation_service import ValidationService, ImageValidator
from app.core.errors.auth import EmailValidationError
from app.core.errors.validation import (
    IdentificatorIsNullError,
    PasswordValidationError,
    UsernameValidationError,
    ImageValidationError, 
    ImageExtensionValidationError
)


class FakeConfig:
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_SPEC_SYMBOLS = "!@#$%^&*()_+-="
    USERNAME_MIN_LENGTH = 3
    USERNAME_MAX_LENGTH = 20
    EMAIL_MAX_LENGTH = 254
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}


class FakeUploadFile:
    def __init__(self, filename: str | None):
        self.filename = filename


@pytest.fixture
def service() -> ValidationService:
    return ValidationService(config_instance=FakeConfig())

@pytest.fixture
def image_validator() -> ImageValidator:
    return ImageValidator(config=FakeConfig())


# validate_password
def test_validate_password_empty_raises(service: ValidationService):
    with pytest.raises(PasswordValidationError):
        service.validate_password("")


def test_validate_password_too_short_raises(service: ValidationService):
    with pytest.raises(PasswordValidationError) as exc:
        service.validate_password("Aa1!")  # len < 8
    assert "минимум" in str(exc.value)


def test_validate_password_whitespace_raises(service: ValidationService):
    with pytest.raises(PasswordValidationError):
        service.validate_password("Aa1! aa1")


def test_validate_password_requires_digit(service: ValidationService):
    with pytest.raises(PasswordValidationError) as exc:
        service.validate_password("Aa!aaaaa")
    assert "цифру" in str(exc.value)


def test_validate_password_requires_upper(service: ValidationService):
    with pytest.raises(PasswordValidationError) as exc:
        service.validate_password("aa1!aaaa")
    assert "заглавную" in str(exc.value)


def test_validate_password_requires_lower(service: ValidationService):
    with pytest.raises(PasswordValidationError) as exc:
        service.validate_password("AA1!AAAA")
    assert "строчную" in str(exc.value)


def test_validate_password_requires_special(service: ValidationService):
    with pytest.raises(PasswordValidationError) as exc:
        service.validate_password("Aa1aaaaa")
    assert "спецсимвол" in str(exc.value)


def test_validate_password_ok(service: ValidationService):
    service.validate_password("Aa1!aaaa")  # ok



# validate_username
def test_validate_username_empty_raises(service: ValidationService):
    with pytest.raises(UsernameValidationError):
        service.validate_username("")


def test_validate_username_too_short_raises(service: ValidationService):
    with pytest.raises(UsernameValidationError):
        service.validate_username("ab")


def test_validate_username_too_long_raises(service: ValidationService):
    with pytest.raises(UsernameValidationError):
        service.validate_username("a" * 21)


def test_validate_username_bad_chars_raises(service: ValidationService):
    with pytest.raises(UsernameValidationError):
        service.validate_username("имя")

    with pytest.raises(UsernameValidationError):
        service.validate_username("name space")

    with pytest.raises(UsernameValidationError):
        service.validate_username("name!")


def test_validate_username_ok(service: ValidationService):
    service.validate_username("user_name-123")



# validate_email
def test_validate_email_empty_raises(service: ValidationService):
    with pytest.raises(EmailValidationError):
        service.validate_email("")


def test_validate_email_too_long_raises(service: ValidationService):
    email = ("a" * 245) + "@b.com"  # >254
    with pytest.raises(EmailValidationError):
        service.validate_email(email)


def test_validate_email_bad_format_raises(service: ValidationService):
    with pytest.raises(EmailValidationError):
        service.validate_email("not-an-email")

    with pytest.raises(EmailValidationError):
        service.validate_email("a@b")

    with pytest.raises(EmailValidationError):
        service.validate_email("@b.com")


def test_validate_email_ok(service: ValidationService):
    service.validate_email("User.Name+tag@example.com")



# validate_credentials
def test_validate_credentials_identifier_none_raises(service: ValidationService):
    with pytest.raises(IdentificatorIsNullError):
        service.validate_credentials(None, "Aa1!aaaa", is_email=True)


def test_validate_credentials_identifier_blank_raises(service: ValidationService):
    with pytest.raises(IdentificatorIsNullError):
        service.validate_credentials("   ", "Aa1!aaaa", is_email=False)


def test_validate_credentials_email_path_lowercase(monkeypatch):
    svc = ValidationService(config_instance=FakeConfig())

    calls = {"email": None}

    def spy_validate_email(self, e: str) -> None:
        calls["email"] = e

    monkeypatch.setattr(ValidationService, "validate_email", spy_validate_email, raising=True)

    svc.validate_credentials("USER@EXAMPLE.COM", "Aa1!aaaa", is_email=True)
    assert calls["email"] == "user@example.com"


def test_validate_credentials_username_path(monkeypatch):
    svc = ValidationService(config_instance=FakeConfig)

    calls = {"username": None}

    def spy_validate_username(self, u: str) -> None:
        calls["username"] = u

    monkeypatch.setattr(ValidationService, "validate_username", spy_validate_username, raising=True)

    svc.validate_credentials("User_1", "Aa1!aaaa", is_email=False)
    assert calls["username"] == "User_1"


def test_validate_credentials_calls_password_validation(monkeypatch):
    svc = ValidationService(config_instance=FakeConfig)

    called = {"n": 0}

    def spy_validate_password(self, p: str) -> None:
        called["n"] += 1

    monkeypatch.setattr(ValidationService, "validate_password", spy_validate_password, raising=True)

    svc.validate_credentials("user@example.com", "Aa1!aaaa", is_email=True)
    assert called["n"] == 1



# validate_image_file
def test_validate_image_file_empty_filename_raises(image_validator: ImageValidator):
    with pytest.raises(ImageValidationError):
        image_validator.validate_image_file(FakeUploadFile(None))

    with pytest.raises(ImageValidationError):
        image_validator.validate_image_file(FakeUploadFile(""))


def test_validate_image_file_bad_extension_raises(image_validator: ImageValidator):
    with pytest.raises(ImageExtensionValidationError) as exc:
        image_validator.validate_image_file(FakeUploadFile("file.exe"))
    assert "Разрешены" in str(exc.value)


class FakeImageFile:
    def __init__(self, filename: str, content: bytes):
        self.filename = filename
        self.file = io.BytesIO(content)

@pytest.fixture
def image_validator():
    class FakeConfig:
        ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
    return ImageValidator(FakeConfig())

PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
    b"\x00\x00\nIDATx\xdac``\x00\x00\x00\x02\x00\x01"
    b"\xe2!\xbc\x33\x00\x00\x00\x00IEND\xaeB`\x82"
)

def test_validate_image_file_ok(image_validator):
    for fname in ["test.jpg", "test.jpeg", "test.png"]:
        file = FakeImageFile(fname, PNG_BYTES)
        image_validator.validate_image_file(file)