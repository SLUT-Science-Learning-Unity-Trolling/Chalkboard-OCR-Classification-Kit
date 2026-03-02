from bson import ObjectId
from app.core.domain.models.user import User


def test_user_id_property_returns_string():
    obj_id = ObjectId("65f000000000000000000300")

    user = User(
        _id=obj_id,
        username="john",
        email="john@example.com",
        password_hash="hashed",
    )

    assert user.id == "65f000000000000000000300"
    assert isinstance(user.id, str)


def test_user_id_property_is_stable():
    obj_id = ObjectId()

    user = User(
        _id=obj_id,
        username="x",
        email="x@example.com",
        password_hash="h",
    )

    first = user.id
    second = user.id

    assert first == second