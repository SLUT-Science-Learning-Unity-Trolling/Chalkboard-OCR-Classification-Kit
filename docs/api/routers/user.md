# Модуль user

Модуль содержит эндпоинты для работы с пользователями.

## def create_user:
#### Эндпоинт создания пользователя.
#### Маршруты:
- `@post( "/users/create", status_code=HTTP_201_CREATED, dto=DataclassDTO[UserCreateDTO], return_dto=DataclassDTO[UserDTO], )`

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `data` | `UserCreateDTO` | Данные для создания пользователя |
| `container` | `Container` | Контейнер |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `UserDTO` | Данные пользователя |

```python
@post(
    "/users/create",
    status_code=HTTP_201_CREATED,
    dto=DataclassDTO[UserCreateDTO],
    return_dto=DataclassDTO[UserDTO],
)
async def create_user(
    data: UserCreateDTO,
    container: Container,
) -> UserDTO:
    """Эндпоинт создания пользователя.

    Args:
        data (UserCreateDTO): Данные для создания пользователя
        container (Container): Контейнер

    Returns:
        UserDTO: Данные пользователя
    """
    user_service = container.resolve(UserService)
    try:
        user: User = await user_service.create_user(
            username=data.username,
            email=data.email,
            password=data.password,
            repeat_password=data.repeat_password,
        )
        return UserDTO.fromrow(user.__dict__)

    except (
        PasswordDontMatchError,
        PasswordValidationError,
        EmailValidationError,
        UsernameValidationError,
        EmailAlreadyTakenError,
        UsernameAlreadyTakenError,
    ) as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e)) from e
```
---