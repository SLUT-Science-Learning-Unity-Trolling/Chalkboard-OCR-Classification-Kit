import pytest
from app.core.services.security_service import SecurityService


class FakeUtils:
    """Фейковая версия jam.utils для изоляции тестов."""

    def __init__(self):
        self.called = {}

    def hash_password(self, password, salt_size):
        self.called["hash_password"] = (password, salt_size)
        return ("FAKE_SALT", "FAKE_HASH")

    def serialize_hash(self, salt, hash_):
        self.called["serialize_hash"] = (salt, hash_)
        return f"{salt}:{hash_}"

    def deserialize_hash(self, data):
        self.called["deserialize_hash"] = (data,)
        # В реальности data сериализовано, возвращаем tuple
        return ("FAKE_SALT", "FAKE_HASH")

    def check_password(self, password, hash_, salt):
        self.called["check_password"] = (password, hash_, salt)
        return password == "ok" and hash_ == "FAKE_HASH" and salt == "FAKE_SALT"


@pytest.fixture
def svc(monkeypatch):
    """Создаём SecurityService с подменённым jam.utils."""
    fake = FakeUtils()
    monkeypatch.setattr("app.core.services.security_service.utils", fake)
    return SecurityService(), fake


def test_hash_password_calls_utils(svc):
    service, fake = svc
    salt, hash_ = service.hash_password("123")
    assert (salt, hash_) == ("FAKE_SALT", "FAKE_HASH")
    assert fake.called["hash_password"] == ("123", 36)


def test_serialize_hash_works(svc):
    service, fake = svc
    result = service.serialize_hash("A", "B")
    assert result == "A:B"
    assert fake.called["serialize_hash"] == ("A", "B")


def test_deserialize_hash_works(svc):
    service, fake = svc
    result = service.deserialize_hash("SALT:HASH")
    assert result == ("FAKE_SALT", "FAKE_HASH")
    assert fake.called["deserialize_hash"] == ("SALT:HASH",)


def test_verify_hash_true_and_false(svc):
    service, fake = svc

    # Валидный пароль
    assert service.verify_hash("ok", "FAKE_SALT", "FAKE_HASH") is True
    # Неверный пароль
    assert service.verify_hash("bad", "FAKE_SALT", "FAKE_HASH") is False

    # Проверим, что вызывалась функция check_password
    assert fake.called["check_password"][0] == "bad"
