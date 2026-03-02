import pytest

from app.api.exceptions.problem_factory import ErrorCodes


@pytest.mark.parametrize(
    ("enum_item", "code", "title", "status"),
    [
        (
            ErrorCodes.SERVICE_CONNECTION_ERROR,
            "service-connection-error",
            "Ошибка подключения к сервису",
            500,
        ),
        (
            ErrorCodes.VALIDATION_ERROR,
            "validation-error",
            "Ошибка валидации данных",
            400,
        ),
        (
            ErrorCodes.AUTHENTICATION_ERROR,
            "authentication-error",
            "Ошибка аутентификации",
            401,
        ),
        (
            ErrorCodes.AUTHORIZATION_ERROR,
            "authorization-error",
            "Ошибка авторизации",
            403,
        ),
        (
            ErrorCodes.IMAGE_UPLOAD_ERROR,
            "image-upload-error",
            "Ошибка загрузки изображения",
            400,
        ),
        (
            ErrorCodes.IMAGE_DELETION_ERROR,
            "delete-image-error",
            "Ошибка удаления изображения",
            400,
        ),
        (
            ErrorCodes.TOO_MANY_REQUESTS_ERROR,
            "too-many-requests-error",
            "Слишком много запросов",
            429,
        ),
    ],
)
def test_error_codes_fields(enum_item: ErrorCodes, code: str, title: str, status: int) -> None:
    assert enum_item.code == code
    assert enum_item.title == title
    assert enum_item.status == status


def test_example_generates_problem_details_dict() -> None:
    detail = "Некорректный email"
    body = ErrorCodes.VALIDATION_ERROR.example(detail)

    assert body == {
        "type": "https://example.com/probs/validation-error",
        "title": "Ошибка валидации данных",
        "status": 400,
        "detail": "Некорректный email",
    }


def test_example_detail_is_not_modified() -> None:
    detail = "  spaces and symbols: !@#  "
    body = ErrorCodes.AUTHENTICATION_ERROR.example(detail)
    assert body["detail"] == detail


def test_example_has_expected_keys() -> None:
    body = ErrorCodes.AUTHORIZATION_ERROR.example("no access")
    assert set(body.keys()) == {"type", "title", "status", "detail"}