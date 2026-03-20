import pytest
from unittest.mock import MagicMock
from litestar import Request, Response

from app.api.exceptions.handlers import (
    ErrorCode,
    create_problem_response,
    create_handler,
    too_many_requests_handler,
    EXCEPTION_HANDLERS,
)

from app.api.exceptions.problem_factory import problem_factory

from app.core.errors.security import TooManyRequestsError
from app.core.errors.auth import PasswordDontMatchError, EmailAlreadyTakenError


def test_create_problem_response_sets_status_and_media_type():
    body = problem_factory.build(ErrorCode.CONFLICT_ERROR, "conflict")
    resp = create_problem_response(body)

    assert isinstance(resp, Response)
    assert resp.status_code == body["status"]
    assert resp.media_type == "application/problem+json"
    assert resp.content == body


def test_create_handler_uses_exc_message_attr_when_present():
    class MyExc(Exception):
        def __init__(self, message: str):
            super().__init__("ignored")
            self.message = message

    handler = create_handler(ErrorCode.AUTHENTICATION_ERROR)
    resp = handler(request=MagicMock(spec=Request), exc=MyExc("nope"))

    assert isinstance(resp, Response)
    assert resp.status_code == 401
    assert resp.media_type == "application/problem+json"
    assert resp.content["detail"] == "nope"


def test_create_handler_falls_back_to_str_exc_when_no_message_attr():
    handler = create_handler(ErrorCode.SERVER_ERROR)
    resp = handler(request=MagicMock(spec=Request), exc=Exception("boom"))

    assert isinstance(resp, Response)
    assert resp.status_code == 500
    assert resp.media_type == "application/problem+json"
    assert resp.content["detail"] == "boom"


def test_too_many_requests_handler_without_retry_after():
    exc = TooManyRequestsError("slow down")
    exc.retry_after = None  # явно задаём

    resp = too_many_requests_handler(request=MagicMock(spec=Request), exc=exc)

    assert isinstance(resp, Response)
    assert resp.status_code == 429
    assert resp.media_type == "application/problem+json"
    assert "Retry-After" not in (resp.headers or {})
    assert "retry_after" not in resp.content


def test_too_many_requests_handler_with_retry_after():
    exc = TooManyRequestsError("slow down")
    exc.retry_after = 10

    resp = too_many_requests_handler(request=MagicMock(spec=Request), exc=exc)

    assert isinstance(resp, Response)
    assert resp.status_code == 429
    assert resp.media_type == "application/problem+json"
    assert (resp.headers or {}).get("Retry-After") == "10"
    assert resp.content["retry_after"] == 10


def test_exception_handlers_mapping_contains_expected_keys():
    assert PasswordDontMatchError in EXCEPTION_HANDLERS
    assert EmailAlreadyTakenError in EXCEPTION_HANDLERS
    assert TooManyRequestsError in EXCEPTION_HANDLERS
    assert EXCEPTION_HANDLERS[TooManyRequestsError] is too_many_requests_handler


def test_exception_handlers_use_correct_handler_type():
    handler = EXCEPTION_HANDLERS[PasswordDontMatchError]

    resp = handler(
        request=MagicMock(spec=Request),
        exc=PasswordDontMatchError("bad password"),
    )

    assert isinstance(resp, Response)
    assert resp.status_code == 400
    assert resp.media_type == "application/problem+json"