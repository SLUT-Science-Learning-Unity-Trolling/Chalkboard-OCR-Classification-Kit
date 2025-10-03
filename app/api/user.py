from litestar import post
from litestar.exceptions import HTTPException
from litestar.params import Parameter
from litestar.response import Response
from litestar.status_codes import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from app.core.services.user_service import UserService
from app.errors.auth import (
    EmailAlreadyTaken,
    EmailValidationError,
    PasswordDontMatch,
)
from app.errors.security import PasswordValidationError
from app.errors.user import UserCreationError
from app.schema.user_dto import UserDTO


@post("/users", status_code=HTTP_201_CREATED)
async def create_user(
    username: str = Parameter(description="Имя пользователя", min_length=3),
    email: str = Parameter(description="Email", pattern=r"[^@]+@[^@]+\.[^@]+"),
    password: str = Parameter(description="Пароль", min_length=3),
    repeat_password: str = Parameter(
        description="Повторите пароль", min_length=3
    ),
    user_service: UserService = Parameter(description="Сервис пользователей"),
) -> Response[UserDTO]:
    try:
        user = await user_service.create_user(
            username=username,
            email=email,
            password=password,
            repeat_password=repeat_password,
        )
        return Response(
            content=UserDTO(
                id=user.id, username=user.username, email=user.email
            ),
            status_code=HTTP_201_CREATED,
        )
    except (
        PasswordDontMatch,
        PasswordValidationError,
        EmailValidationError,
        EmailAlreadyTaken,
    ) as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
    except UserCreationError:
        raise HTTPException(
            status_code=500, detail="Не удалось создать пользователя"
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error occurred"
        )
