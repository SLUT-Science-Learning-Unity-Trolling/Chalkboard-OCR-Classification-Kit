# Модуль auth

Модуль содержит эндпоинты авторизации и выхода из профиля.

## def auth_user:
#### Эндпоинт для авторизации пользователя с установкой JWT в cookie.
#### Маршруты:
- `@post( "/auth/login", status_code=HTTP_201_CREATED, dto=DataclassDTO[UserLoginDTO], return_dto=DataclassDTO[UserDTO], )`

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `data` | `UserLoginDTO` | Данные для авторизации пользователя |
| `container` | `Container` | Контейнер |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `Response` | Ответ с JWT в cookie |

```python
@post(
    "/auth/login",
    status_code=HTTP_201_CREATED,
    dto=DataclassDTO[UserLoginDTO],
    return_dto=DataclassDTO[UserDTO],
)
async def auth_user(
    data: UserLoginDTO,
    container: Container,
) -> Response:
    """Эндпоинт для авторизации пользователя с установкой JWT в cookie.

    Args:
        data (UserLoginDTO): Данные для авторизации пользователя
        container (Container): Контейнер

    Returns:
        Response: Ответ с JWT в cookie
    """
    auth_service = container.resolve(AuthService)

    try:
        user, token = await auth_service.auth_existing_user(
            identifier=data.identifier,
            password=data.password,
        )

        response = Response({"user": UserDTO.fromrow(user.__dict__)})
        response.set_cookie(
            key="token",
            value=token,
            httponly=True,
            secure=True,
            samesite="strict",
            path="/",
        )
        return response

    except InvalidEmailOrPasswordError:
        raise HTTPException(
            status_code=500, detail="Internal server error occurred"
        ) from None
```
---
## def logout_user:
#### Эндпоинт выхода из профиля.
Удаляет JWT из cookie, разлогинивая пользователя.
#### Маршруты:
- `@post("/auth/logout", status_code=HTTP_200_OK)`

```python
@post("/auth/logout", status_code=HTTP_200_OK)
async def logout_user() -> Response:
    """Эндпоинт выхода из профиля.

    Удаляет JWT из cookie, разлогинивая пользователя.
    """
    response = Response({"detail": "Logged out successfully"})
    response.delete_cookie(
        key="token",
        path="/",
    )

    return response
```
---
## def get_me:
#### Эндпоинт возвращает данные текущего пользователя.
#### Маршруты:
- `@get("/me", dependencies={"current_user": Provide(AuthService.get_current_user)})`

```python
@get("/me", dependencies={"current_user": Provide(AuthService.get_current_user)})
async def get_me(current_user: UserDTO | None) -> dict[str, Any]:
    """Эндпоинт возвращает данные текущего пользователя."""
    if current_user:
        return {"success": True, "user": current_user}

    return {
        "success": False,
        "message": "Пользователь не зарегистрирован или не найден в системе",
    }
```
---