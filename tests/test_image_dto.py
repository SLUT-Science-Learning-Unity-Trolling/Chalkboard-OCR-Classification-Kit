import pytest
from bson import ObjectId

from app.api.schemas.image_dto import ImageDTO


def test_fromrow_with_objectid_and_user_id():
    row = {
        "_id": ObjectId("65f000000000000000000010"),
        "_user_id": ObjectId("65f000000000000000000011"),
        "url": "https://cdn/img.png",
    }

    dto = ImageDTO.fromrow(row)

    assert dto.id == "65f000000000000000000010"
    assert dto.user_id == "65f000000000000000000011"
    assert dto.url == "https://cdn/img.png"


def test_fromrow_with_string_ids():
    row = {
        "id": "img123",
        "user_id": "user456",
        "url": "https://cdn/img.png",
    }

    dto = ImageDTO.fromrow(row)

    assert dto.id == "img123"
    assert dto.user_id == "user456"
    assert dto.url == "https://cdn/img.png"


def test_fromrow_prioritizes_underscore_keys():
    row = {
        "_id": "priority_id",
        "id": "secondary_id",
        "_user_id": "priority_user",
        "user_id": "secondary_user",
        "url": "https://cdn/img.png",
    }

    dto = ImageDTO.fromrow(row)

    assert dto.id == "priority_id"
    assert dto.user_id == "priority_user"


def test_fromrow_missing_url_raises_keyerror():
    row = {
        "_id": "x",
        "_user_id": "y",
    }

    with pytest.raises(KeyError):
        ImageDTO.fromrow(row)