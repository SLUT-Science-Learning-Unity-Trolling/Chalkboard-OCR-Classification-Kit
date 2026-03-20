import pytest
from bson import ObjectId

from app.api.schemas.user_dto import UserDTO


def test_fromrow_with_objectid():
    row = {
        "_id": ObjectId("65f000000000000000000020"),
        "username": "john",
        "email": "john@example.com",
    }

    dto = UserDTO.fromrow(row)

    assert dto.id == "65f000000000000000000020"
    assert dto.username == "john"
    assert dto.email == "john@example.com"


def test_fromrow_with_string_id():
    row = {
        "id": "user123",
        "username": "alice",
        "email": "alice@example.com",
    }

    dto = UserDTO.fromrow(row)

    assert dto.id == "user123"
    assert dto.username == "alice"
    assert dto.email == "alice@example.com"


def test_fromrow_prioritizes_underscore_id():
    row = {
        "_id": "priority_id",
        "id": "secondary_id",
        "username": "bob",
        "email": "bob@example.com",
    }

    dto = UserDTO.fromrow(row)

    assert dto.id == "priority_id"


def test_fromrow_missing_username_raises_keyerror():
    row = {
        "_id": "x",
        "email": "x@example.com",
    }

    with pytest.raises(KeyError):
        UserDTO.fromrow(row)


def test_fromrow_missing_email_raises_keyerror():
    row = {
        "_id": "x",
        "username": "x",
    }

    with pytest.raises(KeyError):
        UserDTO.fromrow(row)