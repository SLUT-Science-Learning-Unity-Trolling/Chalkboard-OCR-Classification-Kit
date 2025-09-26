import pytest

from app.core.models.user import User
from app.schema.user_dto import UserDTO


sample_doc = {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "test_user",
    "email": "test@example.com",
}


def dto_to_domain(dto: UserDTO) -> User:
    return User(**dto.model_dump())


@pytest.mark.benchmark(group="conversion")
def test_dict_to_dto_to_domain(benchmark):
    def convert():
        dto = UserDTO(**sample_doc)  # dict -> DTO
        domain = dto_to_domain(dto)  # DTO -> Domain
        return domain.__dict__  # Domain -> dict

    result = benchmark(convert)
    assert result["username"] == "test_user"
