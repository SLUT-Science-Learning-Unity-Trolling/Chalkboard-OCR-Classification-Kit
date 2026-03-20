import pytest
from app.api.exceptions.problem_factory import ErrorCode, problem_factory

@pytest.mark.parametrize(
    ("enum_item", "code", "title", "status"),
    [
        (ErrorCode.SERVICE_CONNECTION_ERROR, "service-connection-error", "Ошибка подключения к сервису", 500),
        (ErrorCode.VALIDATION_ERROR, "validation-error", "Ошибка валидации данных", 400),
        (ErrorCode.AUTHENTICATION_ERROR, "authentication-error", "Ошибка аутентификации", 401),
        (ErrorCode.AUTHORIZATION_ERROR, "authorization-error", "Ошибка авторизации", 403),
        (ErrorCode.IMAGE_UPLOAD_ERROR, "image-upload-error", "Ошибка загрузки изображения", 400),
        (ErrorCode.IMAGE_DELETION_ERROR, "image-deletion-error", "Ошибка удаления изображения", 400),
        (ErrorCode.TOO_MANY_REQUESTS, "too-many-requests", "Превышен лимит запросов", 429),
    ],
)
def test_error_codes_fields(enum_item: ErrorCode, code: str, title: str, status: int) -> None:
    assert enum_item.value.code == code
    assert enum_item.value.title == title
    assert enum_item.value.status == status


def test_example_generates_problem_details_dict() -> None:
    detail = "Некорректный email"
    body = enum_example(ErrorCode.VALIDATION_ERROR, detail)

    assert body == {
        "type": f"{problem_factory._base_uri}/validation-error",
        "title": "Ошибка валидации данных",
        "status": 400,
        "detail": detail,
    }


def test_example_detail_is_not_modified() -> None:
    detail = "  spaces and symbols: !@#  "
    body = enum_example(ErrorCode.AUTHENTICATION_ERROR, detail)
    assert body["detail"] == detail


def test_example_has_expected_keys() -> None:
    body = enum_example(ErrorCode.AUTHORIZATION_ERROR, "no access")
    assert set(body.keys()) == {"type", "title", "status", "detail"}


def enum_example(error: ErrorCode, detail: str, **extra) -> dict[str, any]:
    return problem_factory.build(error, detail, **extra)