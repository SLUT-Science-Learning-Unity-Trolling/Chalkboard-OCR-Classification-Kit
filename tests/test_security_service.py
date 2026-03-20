from __future__ import annotations

import types

import pytest

from app.core.services.security_service import SecurityService
import app.core.services.security_service as security_service_mod


@pytest.fixture
def fake_utils(monkeypatch):
    """
    Подменяем security_service_mod.utils (то, что реально используется внутри SecurityService).
    Это обходит любые моки из conftest.py.
    """
    u = types.SimpleNamespace()

    def hash_password(password: str, salt_size: int = 36):
        assert salt_size == 36
        return ("salt123", f"hash_of_{password}")

    def serialize_hash(salt: str, hash_: str):
        return f"{salt}:{hash_}"

    def deserialize_hash(data: str):
        salt, hash_ = data.split(":")
        return salt, hash_

    def check_password(password: str, hash_: str, salt: str):
        return hash_ == f"hash_of_{password}"

    u.hash_password = hash_password
    u.serialize_hash = serialize_hash
    u.deserialize_hash = deserialize_hash
    u.check_password = check_password

    monkeypatch.setattr(security_service_mod, "utils", u, raising=True)
    return u


def test_hash_password_returns_salt_and_hash(fake_utils):
    service = SecurityService()
    salt, hash_ = service.hash_password("123")

    assert salt == "salt123"
    assert hash_ == "hash_of_123"


def test_serialize_and_deserialize_roundtrip(fake_utils):
    service = SecurityService()
    salt, hash_ = service.hash_password("abc")

    serialized = service.serialize_hash(salt, hash_)
    salt2, hash2 = service.deserialize_hash(serialized)

    assert salt == salt2
    assert hash_ == hash2


def test_verify_hash_success(fake_utils):
    service = SecurityService()
    salt, hash_ = service.hash_password("password")

    assert service.verify_hash("password", salt, hash_) is True


def test_verify_hash_fail(fake_utils):
    service = SecurityService()
    salt, hash_ = service.hash_password("password")

    assert service.verify_hash("wrong", salt, hash_) is False