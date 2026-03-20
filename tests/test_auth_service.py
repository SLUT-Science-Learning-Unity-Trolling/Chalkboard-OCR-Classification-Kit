from __future__ import annotations

import types
from dataclasses import dataclass
from typing import Any, Dict, cast
from unittest.mock import AsyncMock, Mock

import pytest

from litestar import Request
from punq import Container

from app.api.schemas.user_dto import UserDTO
from app.core.errors.auth import InvalidEmailOrPasswordError, UnauthorizedError
from app.core.errors.security import InvalidTokenError
from app.core.services.auth_service import AuthService


# Helpers / Fakes


@dataclass
class FakeRequest:
    cookies: Dict[str, str]


class FakeContainer:
    """Мини-контейнер под container.resolve(UserService)."""

    def __init__(self, user_service: Any):
        self._user_service = user_service

    def resolve(self, cls: Any) -> Any:
        return self._user_service


# Fixtures


@pytest.fixture
def repo():
    r = Mock()
    r.get_one = AsyncMock()
    return r


@pytest.fixture
def security():
    sec = Mock()
    sec.deserialize_hash = Mock()
    sec.verify_hash = Mock()
    return sec


@pytest.fixture
def validation():
    v = Mock()
    v.validate_credentials = Mock()
    return v


@pytest.fixture
def redis_blacklist():
    bl = Mock()
    bl.is_blacklisted = AsyncMock()
    bl.add_to_blacklist = AsyncMock()
    return bl


@pytest.fixture
def redis_rate_limit():
    # В текущем AuthService не используется, но нужен для конструктора.
    return Mock()


@pytest.fixture
def service(repo, security, validation, redis_blacklist, redis_rate_limit):
    return AuthService(
        repository=repo,
        security=security,
        validation=validation,
        redis_blacklist_repo=redis_blacklist,
        redis_rate_limit_repo=redis_rate_limit,
    )


@pytest.fixture
def paseto_mock(monkeypatch):
    """
    Даём paseto.create/parse без libsodium.
    Патчим paseto внутри модуля, где объявлен AuthService.
    """
    create = Mock()
    parse = Mock()

    auth_module = __import__(AuthService.__module__, fromlist=["paseto"])
    monkeypatch.setattr(
        auth_module, "paseto", types.SimpleNamespace(create=create, parse=parse)
    )

    return types.SimpleNamespace(create=create, parse=parse)


# auth_existing_user


@pytest.mark.asyncio
async def test_auth_existing_user_email_user_not_found(
    service, repo, validation, paseto_mock
):
    repo.get_one.return_value = None

    with pytest.raises(InvalidEmailOrPasswordError):
        await service.auth_existing_user(
            identifier="test@example.com",
            password="password",
            client_ip="127.0.0.1",
        )

    validation.validate_credentials.assert_called_once()
    repo.get_one.assert_awaited_once_with({"email": "test@example.com"})
    assert paseto_mock.create.call_count == 0


@pytest.mark.asyncio
async def test_auth_existing_user_username_user_not_found(
    service, repo, validation, paseto_mock
):
    repo.get_one.return_value = None

    with pytest.raises(InvalidEmailOrPasswordError):
        await service.auth_existing_user(
            identifier="someuser",
            password="password",
            client_ip="127.0.0.1",
        )

    validation.validate_credentials.assert_called_once()
    repo.get_one.assert_awaited_once_with({"username": "someuser"})
    assert paseto_mock.create.call_count == 0


@pytest.mark.asyncio
async def test_auth_existing_user_wrong_password(
    service, repo, security, validation, paseto_mock
):
    repo.get_one.return_value = {
        "_id": "u1",
        "username": "john",
        "email": "john@example.com",
        "password_hash": "serialized",
    }
    security.deserialize_hash.return_value = ("hash", "salt")
    security.verify_hash.return_value = False

    with pytest.raises(InvalidEmailOrPasswordError):
        await service.auth_existing_user(
            identifier="john@example.com",
            password="wrong",
            client_ip="127.0.0.1",
        )

    validation.validate_credentials.assert_called_once()
    security.deserialize_hash.assert_called_once_with("serialized")
    security.verify_hash.assert_called_once_with(password="wrong", salt="salt", hash_="hash")
    assert paseto_mock.create.call_count == 0


@pytest.mark.asyncio
async def test_auth_existing_user_success_returns_dto_and_tokens(
    service, repo, security, validation, paseto_mock
):
    repo.get_one.return_value = {
        "_id": "u1",
        "username": "john",
        "email": "john@example.com",
        "password_hash": "serialized",
    }
    security.deserialize_hash.return_value = ("hash", "salt")
    security.verify_hash.return_value = True

    paseto_mock.create.side_effect = ["ACCESS_TOKEN", "REFRESH_TOKEN"]

    user_dto, access, refresh = await service.auth_existing_user(
        identifier="john@example.com",
        password="correct",
        client_ip="127.0.0.1",
    )

    validation.validate_credentials.assert_called_once()
    repo.get_one.assert_awaited_once_with({"email": "john@example.com"})
    assert paseto_mock.create.call_count == 2

    assert access == "ACCESS_TOKEN"
    assert refresh == "REFRESH_TOKEN"

    assert user_dto.id == "u1"
    assert user_dto.username == "john"
    assert user_dto.email == "john@example.com"

    access_kwargs = paseto_mock.create.call_args_list[0].kwargs
    refresh_kwargs = paseto_mock.create.call_args_list[1].kwargs

    assert access_kwargs["claims"]["type"] == "access"
    assert access_kwargs["claims"]["sub"] == "u1"
    assert access_kwargs["claims"]["username"] == "john"
    assert access_kwargs["claims"]["email"] == "john@example.com"
    assert "jti" in access_kwargs["claims"]

    assert refresh_kwargs["claims"]["type"] == "refresh"
    assert refresh_kwargs["claims"]["sub"] == "u1"
    assert "jti" in refresh_kwargs["claims"]


# get_current_user


@pytest.mark.asyncio
async def test_get_current_user_no_cookie_unauthorized(paseto_mock):
    request = cast(Request, FakeRequest(cookies={}))
    container = cast(Container, FakeContainer(user_service=Mock()))

    with pytest.raises(UnauthorizedError):
        await AuthService.get_current_user(request=request, container=container)

    assert paseto_mock.parse.call_count == 0


@pytest.mark.asyncio
async def test_get_current_user_invalid_paseto_raises_invalid_token(paseto_mock):
    request = cast(Request, FakeRequest(cookies={"access_token": "BAD"}))

    user_service = Mock()
    user_service.get_user_by_id = AsyncMock()
    container = cast(Container, FakeContainer(user_service=user_service))

    paseto_mock.parse.side_effect = Exception("parse failed")

    with pytest.raises(InvalidTokenError):
        await AuthService.get_current_user(request=request, container=container)

    paseto_mock.parse.assert_called_once()


@pytest.mark.asyncio
async def test_get_current_user_wrong_type_raises_invalid_token(paseto_mock):
    request = cast(Request, FakeRequest(cookies={"access_token": "TOKEN"}))

    user_service = Mock()
    user_service.get_user_by_id = AsyncMock()
    container = cast(Container, FakeContainer(user_service=user_service))

    paseto_mock.parse.return_value = {"message": {"type": "refresh", "sub": "u1"}}

    with pytest.raises(InvalidTokenError):
        await AuthService.get_current_user(request=request, container=container)


@pytest.mark.asyncio
async def test_get_current_user_no_sub_raises_invalid_token(paseto_mock):
    request = cast(Request, FakeRequest(cookies={"access_token": "TOKEN"}))

    user_service = Mock()
    user_service.get_user_by_id = AsyncMock()
    container = cast(Container, FakeContainer(user_service=user_service))

    paseto_mock.parse.return_value = {"message": {"type": "access", "sub": ""}}

    with pytest.raises(InvalidTokenError):
        await AuthService.get_current_user(request=request, container=container)


@pytest.mark.asyncio
async def test_get_current_user_user_not_found_unauthorized(paseto_mock):
    request = cast(Request, FakeRequest(cookies={"access_token": "TOKEN"}))

    user_service = Mock()
    user_service.get_user_by_id = AsyncMock(return_value=None)
    container = cast(Container, FakeContainer(user_service=user_service))

    paseto_mock.parse.return_value = {"message": {"type": "access", "sub": "u1"}}

    with pytest.raises(UnauthorizedError):
        await AuthService.get_current_user(request=request, container=container)

    user_service.get_user_by_id.assert_awaited_once_with("u1")


@pytest.mark.asyncio
async def test_get_current_user_success_returns_dto(monkeypatch, paseto_mock):
    request = cast(Request, FakeRequest(cookies={"access_token": "TOKEN"}))

    fake_user_row = {"_id": "u1", "username": "john", "email": "john@example.com"}

    user_service = Mock()
    user_service.get_user_by_id = AsyncMock(return_value=fake_user_row)
    container = cast(Container, FakeContainer(user_service=user_service))

    paseto_mock.parse.return_value = {"message": {"type": "access", "sub": "u1"}}

    class _DTO:
        def __init__(self, id: str, username: str, email: str):
            self.id = id
            self.username = username
            self.email = email

    def _fromrow(row: dict[str, Any]):
        return _DTO(id=str(row["_id"]), username=row["username"], email=row["email"])

    monkeypatch.setattr(UserDTO, "fromrow", staticmethod(_fromrow))

    dto = await AuthService.get_current_user(request=request, container=container)

    assert dto.id == "u1"
    assert dto.username == "john"
    assert dto.email == "john@example.com"


# refresh_tokens


@pytest.mark.asyncio
async def test_refresh_tokens_no_refresh_unauthorized(service, paseto_mock):
    with pytest.raises(UnauthorizedError):
        await service.refresh_tokens(
            refresh_token="",
            access_token=None,
            client_ip="127.0.0.1",
        )

    assert paseto_mock.parse.call_count == 0


@pytest.mark.asyncio
async def test_refresh_tokens_refresh_parse_fails(service, paseto_mock):
    paseto_mock.parse.side_effect = Exception("parse failed")

    with pytest.raises(UnauthorizedError) as exc:
        await service.refresh_tokens(
            refresh_token="BAD",
            access_token=None,
            client_ip="127.0.0.1",
        )

    assert "Неизвестный refresh токен" in str(exc.value)


@pytest.mark.asyncio
async def test_refresh_tokens_refresh_wrong_type(service, paseto_mock):
    paseto_mock.parse.return_value = {"message": {"type": "access", "jti": "r1", "sub": "u1"}}

    with pytest.raises(UnauthorizedError) as exc:
        await service.refresh_tokens(
            refresh_token="R",
            access_token=None,
            client_ip="127.0.0.1",
        )

    assert "Тип токена не соответствует refresh" in str(exc.value)


@pytest.mark.asyncio
async def test_refresh_tokens_refresh_no_jti(service, paseto_mock):
    paseto_mock.parse.return_value = {"message": {"type": "refresh", "sub": "u1"}}

    with pytest.raises(UnauthorizedError) as exc:
        await service.refresh_tokens(
            refresh_token="R",
            access_token=None,
            client_ip="127.0.0.1",
        )

    assert "Refresh в токене отсутствует jti" in str(exc.value)


@pytest.mark.asyncio
async def test_refresh_tokens_refresh_blacklisted(service, redis_blacklist, paseto_mock):
    paseto_mock.parse.return_value = {"message": {"type": "refresh", "sub": "u1", "jti": "rjti"}}
    redis_blacklist.is_blacklisted.return_value = True

    with pytest.raises(UnauthorizedError) as exc:
        await service.refresh_tokens(
            refresh_token="R",
            access_token=None,
            client_ip="127.0.0.1",
        )

    assert "Refresh токен в чёрном списке" in str(exc.value)
    redis_blacklist.is_blacklisted.assert_awaited_once_with("rjti")


@pytest.mark.asyncio
async def test_refresh_tokens_access_blacklisted(service, redis_blacklist, paseto_mock):
    paseto_mock.parse.side_effect = [
        {"message": {"type": "refresh", "sub": "u1", "jti": "rjti"}},
        {"message": {"type": "access", "sub": "u1", "jti": "ajti"}},
    ]
    redis_blacklist.is_blacklisted.side_effect = [False, True]

    with pytest.raises(UnauthorizedError) as exc:
        await service.refresh_tokens(
            refresh_token="R",
            access_token="A",
            client_ip="127.0.0.1",
        )

    assert "Access токен в чёрном списке" in str(exc.value)
    assert redis_blacklist.is_blacklisted.await_count == 2


@pytest.mark.asyncio
async def test_refresh_tokens_success_blacklists_old_jtis_and_returns_new_tokens(
    service, redis_blacklist, paseto_mock
):
    paseto_mock.parse.side_effect = [
        {"message": {"type": "refresh", "sub": "u1", "jti": "rjti"}},
        {"message": {"type": "access", "sub": "u1", "jti": "ajti"}},
    ]
    redis_blacklist.is_blacklisted.side_effect = [False, False]

    paseto_mock.create.side_effect = ["NEW_ACCESS", "NEW_REFRESH"]

    new_access, new_refresh = await service.refresh_tokens(
        refresh_token="R",
        access_token="A",
        client_ip="127.0.0.1",
    )

    assert new_access == "NEW_ACCESS"
    assert new_refresh == "NEW_REFRESH"

    assert redis_blacklist.add_to_blacklist.await_count == 2

    call1_args = redis_blacklist.add_to_blacklist.await_args_list[0].args
    call2_args = redis_blacklist.add_to_blacklist.await_args_list[1].args
    assert call1_args[0] == "rjti"
    assert call2_args[0] == "ajti"


@pytest.mark.asyncio
async def test_refresh_tokens_success_without_access_token_blacklists_only_refresh(
    service, redis_blacklist, paseto_mock
):
    paseto_mock.parse.return_value = {"message": {"type": "refresh", "sub": "u1", "jti": "rjti"}}
    redis_blacklist.is_blacklisted.return_value = False

    paseto_mock.create.side_effect = ["NEW_ACCESS", "NEW_REFRESH"]

    new_access, new_refresh = await service.refresh_tokens(
        refresh_token="R",
        access_token=None,
        client_ip="127.0.0.1",
    )

    assert new_access == "NEW_ACCESS"
    assert new_refresh == "NEW_REFRESH"

    redis_blacklist.add_to_blacklist.assert_awaited_once()
    args = redis_blacklist.add_to_blacklist.await_args.args
    assert args[0] == "rjti"


# _blacklist_token


@pytest.mark.asyncio
async def test_blacklist_token_invalid_token_raises_invalidtoken(service, paseto_mock):
    paseto_mock.parse.side_effect = Exception("parse failed")

    with pytest.raises(InvalidTokenError):
        await service._blacklist_token(token="BAD", expected_type="refresh", expires_in=10)


@pytest.mark.asyncio
async def test_blacklist_token_type_mismatch_does_nothing(service, redis_blacklist, paseto_mock):
    paseto_mock.parse.return_value = {"message": {"type": "access", "jti": "t1"}}

    await service._blacklist_token(token="TOKEN", expected_type="refresh", expires_in=10)

    redis_blacklist.add_to_blacklist.assert_not_awaited()


@pytest.mark.asyncio
async def test_blacklist_token_no_jti_does_nothing(service, redis_blacklist, paseto_mock):
    paseto_mock.parse.return_value = {"message": {"type": "refresh"}}

    await service._blacklist_token(token="TOKEN", expected_type="refresh", expires_in=10)

    redis_blacklist.add_to_blacklist.assert_not_awaited()


@pytest.mark.asyncio
async def test_blacklist_token_success_adds_to_blacklist(service, redis_blacklist, paseto_mock):
    paseto_mock.parse.return_value = {"message": {"type": "refresh", "jti": "t1"}}

    await service._blacklist_token(token="TOKEN", expected_type="refresh", expires_in=123)

    redis_blacklist.add_to_blacklist.assert_awaited_once_with("t1", expires_in=123)