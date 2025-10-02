from litestar import Litestar, get, post
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.openapi import OpenAPIConfig
from litestar.params import Parameter
from litestar.response import Response
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
)

from app.container import build_container
from app.core.services.user_service import UserService
from app.errors.auth import (
    EmailAlreadyTaken,
    EmailValidationError,
    PasswordDontMatch,
)
from app.errors.security import PasswordValidationError
from app.errors.user import UserCreationError
from app.schema.user_dto import UserDTO


async def provide_user_service() -> UserService:
    container = build_container()
    return container.resolve(UserService)


@post("/user", status_code=HTTP_201_CREATED)
async def create_user(
    username: str = Parameter(description="Имя пользователя", min_length=3),
    email: str = Parameter(
        description="Email пользователя", pattern=r"[^@]+@[^@]+\.[^@]+"
    ),
    password: str = Parameter(description="Пароль пользователя", min_length=3),
    repeat_password: str = Parameter(
        description="Повторите пароль", min_length=3
    ),
    user_service: UserService = Parameter(description="Сервис пользователей"),
) -> Response[UserDTO]:
    """Создание нового пользователя."""
    try:
        user = await user_service.create_user(
            username=username,
            email=email,
            password=password,
            repeat_password=repeat_password,
        )
        return Response(
            content=UserDTO(
                id=user.id,
                username=user.username,
                email=user.email,
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


@get("/health", status_code=HTTP_200_OK)
async def health_check() -> dict:
    """Проверка работоспособности сервиса."""
    return {"status": "healthy"}


openapi_config = OpenAPIConfig(
    title="COCK API",
    version="1.0.0",
    description="Chalkboard OCR Classification Kit API",
)

app = Litestar(
    route_handlers=[create_user, health_check],
    dependencies={"user_service": Provide(provide_user_service)},
    openapi_config=openapi_config,
    debug=True,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
