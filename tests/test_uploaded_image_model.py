import pytest
from bson import ObjectId

from app.core.domain.models.image import UploadedImage


def test_id_property_returns_string():
    obj_id = ObjectId("65f000000000000000000200")
    user_id = ObjectId("65f000000000000000000201")

    image = UploadedImage(
        _id=obj_id,
        _user_id=user_id,
        url="https://cdn/image.png",
        uploaded_at=1234567890,
    )

    assert image.id == "65f000000000000000000200"


def test_user_id_property_currently_raises_recursionerror():
    """
    Текущее поведение модели (баг): user_id вызывает сам себя:
        return str(self.user_id)
    Поэтому происходит RecursionError.
    Так как "ничего менять нельзя", тест фиксирует этот факт.
    """
    obj_id = ObjectId("65f000000000000000000200")
    user_id = ObjectId("65f000000000000000000201")

    image = UploadedImage(
        _id=obj_id,
        _user_id=user_id,
        url="https://cdn/image.png",
        uploaded_at=1234567890,
    )

    with pytest.raises(RecursionError):
        _ = image.user_id


def test_properties_do_not_break_id_but_user_id_is_known_bug():
    """
    id должен работать всегда.
    user_id на текущей реализации падает (известный дефект).
    """
    image = UploadedImage(
        _id=ObjectId(),
        _user_id=ObjectId(),
        url="x",
        uploaded_at=1,
    )

    _ = image.id

    with pytest.raises(RecursionError):
        _ = image.user_id