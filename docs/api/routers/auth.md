# Модуль auth

Модуль содержит эндпоинты авторизации и выхода из профиля.

## def auth_user:
#### Эндпоинт для авторизации пользователя с установкой PASETO в cookie.
#### Маршрут:
- **Декоратор:** @post
- **Маршрут:** `/login`
- **Заголовок:** Авторизация пользователя
- **Описание:** Эндпоинт для авторизации пользователя с установкой Paseto в cookie.Принимает email или username и пароль, возвращает данные пользователя и устанавливает access и refresh токены в cookie.
- **Теги:** Авторизация


#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `data` | `UserLoginDTO` | Данные для авторизации пользователя |
| `container` | `Container` | Контейнер |
| `request` | `Request` | HTTP запрос для получения IP клиента |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `Response` | Ответ с PASETO в cookie |

```python
@post(
    "/login",
    summary="Авторизация пользователя",
    description="Эндпоинт для авторизации пользователя с установкой Paseto в cookie."
    "Принимает email или username и пароль, возвращает данные пользователя и устанавливает access и refresh токены в cookie.",
    tags=["Авторизация"],
    status_code=HTTP_200_OK,
    dto=DataclassDTO[UserLoginDTO],
    return_dto=DataclassDTO[UserDTO],
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Пользователь авторизован",
            data_container=UserDTO,
            examples=[
                Example(
                    value={
                        "id": "694de2b36e5be2ab74f350e6",
                        "username": "User123",
                        "email": "user@example.com",
                    },
                )
            ],
        ),
        HTTP_401_UNAUTHORIZED: ResponseSpec(
            description="Неверные данные",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.AUTHENTICATION_ERROR.example(
                        "Неверная почта/логин или пароль"
                    ),
                )
            ],
        ),
        HTTP_400_BAD_REQUEST: ResponseSpec(
            description="Невалидные данные",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.VALIDATION_ERROR.example(
                        "Ошибка валидации данных"
                    ),
                )
            ],
        ),
        HTTP_500_INTERNAL_SERVER_ERROR: ResponseSpec(
            description="Внутренняя ошибка сервера",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.SERVICE_CONNECTION_ERROR.example(
                        "Внутренняя ошибка сервера"
                    ),
                )
            ],
        ),
        HTTP_429_TOO_MANY_REQUESTS: ResponseSpec(
            description="Слишком много запросов",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.TOO_MANY_REQUESTS_ERROR.example(
                        "Слишком много попыток авторизации. Попробуйте позже."
                    ),
                )
            ],
        ),
    },
)
async def auth_user(
    data: UserLoginDTO,
    container: Container,
    request: Request,
) -> Response:
    """Эндпоинт для авторизации пользователя с установкой PASETO в cookie.

    Args:
        data (UserLoginDTO): Данные для авторизации пользователя
        container (Container): Контейнер
        request (Request): HTTP запрос для получения IP клиента

    Returns:
        Response: Ответ с PASETO в cookie
    """
    auth_service = container.resolve(AuthService)

    client_ip = request.client.host

    user, access_token, refresh_token = await auth_service.auth_existing_user(
        identifier=data.identifier,
        password=data.password,
        client_ip=client_ip,
    )

    user_dto = UserDTO.fromrow(user.__dict__)

    response = Response(user_dto)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        max_age=config.ACCESS_TOKEN_EXPIRE_TIME,
        samesite="strict",
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        max_age=config.REFRESH_TOKEN_EXPIRE_TIME,
        samesite="strict",
        path="/auth",
    )
    return response
```
---
## def logout_user:
#### Эндпоинт выхода из профиля.

Производит:
- Удаление access и refresh токенов из cookie.
- Добавление токенов в blacklist на сервере.
#### Маршрут:
- **Декоратор:** @post
- **Маршрут:** `/logout`
- **Заголовок:** Выход из профиля
- **Описание:** Эндпоинт выхода из профиля. Удаляет Paseto из cookie
- **Теги:** Авторизация


#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `request` | `Request` | HTTP-запрос. |
| `container` | `Container` | DI-контейнер для получения сервисов. |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `Response` | Подтверждение успешного выхода с удалением cookie. |

```python
@post(
    "/logout",
    summary="Выход из профиля",
    description="Эндпоинт выхода из профиля. Удаляет Paseto из cookie",
    tags=["Авторизация"],
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Пользователь успешно вышел из аккаунта",
            data_container=None,
        ),
    },
)
async def logout_user(request: Request, container: Container) -> Response:
    """Эндпоинт выхода из профиля.

    Производит:
        - Удаление access и refresh токенов из cookie.
        - Добавление токенов в blacklist на сервере.

    Args:
        request (Request): HTTP-запрос.
        container (Container): DI-контейнер для получения сервисов.

    Returns:
        Response: Подтверждение успешного выхода с удалением cookie.
    """
    auth_service = container.resolve(AuthService)

    refresh_token = request.cookies.get("refresh_token")
    access_token = request.cookies.get("access_token")

    if refresh_token:
        await auth_service._blacklist_token(
            token=refresh_token,
            expected_type="refresh",
            expires_in=config.REFRESH_TOKEN_EXPIRE_TIME,
        )

    if access_token:
        await auth_service._blacklist_token(
            token=access_token,
            expected_type="access",
            expires_in=config.ACCESS_TOKEN_EXPIRE_TIME,
        )

    response = Response(
        content={"detail": "Пользователь успешно вышел из аккаунта"},
        status_code=HTTP_200_OK,
    )
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/auth")

    return response
```
---
## def get_me:
#### Эндпоинт возвращает информацию о текущем пользователе.
#### Маршрут:
- **Декоратор:** @get
- **Маршрут:** `/me`
- **Заголовок:** Данные текущего пользователя
- **Описание:** Эндпоинт возвращает данные текущего авторизованного пользователя
- **Теги:** Debug, Авторизация


#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `current_user` | `UserDTO \| None` | Объект текущего пользователя, предоставляемый зависимостью. |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `UserDTO` | Данные текущего авторизованного пользователя. |

```python
@get(
    "/me",
    summary="Данные текущего пользователя",
    description="Эндпоинт возвращает данные текущего авторизованного пользователя",
    tags=["Debug", "Авторизация"],
    dependencies={"current_user": Provide(AuthService.get_current_user)},
    status_code=HTTP_200_OK,
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Пользователь авторизован",
            data_container=UserDTO,
            examples=[
                Example(
                    value={
                        "id": "694de2b36e5be2ab74f350e6",
                        "username": "User123",
                        "email": "user@example.com",
                    },
                )
            ],
        ),
        HTTP_401_UNAUTHORIZED: ResponseSpec(
            description="Пользователь не авторизован",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.AUTHORIZATION_ERROR.example(
                        "Пользователь не авторизован или сессия истекла"
                    ),
                )
            ],
        ),
        HTTP_429_TOO_MANY_REQUESTS: ResponseSpec(
            description="Слишком много запросов",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.TOO_MANY_REQUESTS_ERROR.example(
                        "Слишком много попыток авторизации. Попробуйте позже."
                    ),
                )
            ],
        ),
    },
)
async def get_me(current_user: UserDTO | None) -> UserDTO:
    """Эндпоинт возвращает информацию о текущем пользователе.

    Args:
        current_user (UserDTO | None): Объект текущего пользователя, предоставляемый зависимостью.

    Returns:
        UserDTO: Данные текущего авторизованного пользователя.
    """
    return current_user
```
---
## def refresh_user:
#### Эндпоинт обновляет access токен по refresh токену.

Получает refresh токен из cookie, проверяет его валидность и выдает новый access токен.
#### Маршрут:
- **Декоратор:** @post
- **Маршрут:** `/refresh`
- **Заголовок:** Обновление access токена
- **Описание:** Эндпоинт обновляет access токен по refresh токену
- **Теги:** Авторизация


#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `request` | `Request` | HTTP запрос с refresh токеном в |
| `container` | `Container` | Контейнер для получения сервисов |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `Response` | Ответ с новым access токеном в cookie |

```python
@post(
    "/refresh",
    summary="Обновление access токена",
    description="Эндпоинт обновляет access токен по refresh токену",
    status_code=HTTP_200_OK,
    tags=["Авторизация"],
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Токены успешно обновлены",
            data_container=None,
        ),
        HTTP_401_UNAUTHORIZED: ResponseSpec(
            description="Невалидный refresh токен",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.AUTHENTICATION_ERROR.example(
                        "Невалидный или просроченный refresh токен"
                    ),
                )
            ],
        ),
        HTTP_429_TOO_MANY_REQUESTS: ResponseSpec(
            description="Слишком много попыток авторизации",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.TOO_MANY_REQUESTS_ERROR.example(
                        "Слишком много попыток обновления токенов. Попробуйте позже."
                    ),
                )
            ],
        ),
    },
)
async def refresh_user(request: Request, container: Container) -> Response:
    """Эндпоинт обновляет access токен по refresh токену.

    Получает refresh токен из cookie, проверяет его валидность и выдает новый access токен.

    Args:
        request (Request): HTTP запрос с refresh токеном в
        container (Container): Контейнер для получения сервисов

    Returns:
        Response: Ответ с новым access токеном в cookie
    """
    auth_service = container.resolve(AuthService)

    client_ip = request.client.host

    refresh_token = request.cookies.get("refresh_token")
    access_token = request.cookies.get("access_token")

    new_access, new_refresh = await auth_service.refresh_tokens(
        refresh_token, access_token, client_ip
    )

    response = Response({"detail": "Token refreshed"})

    response.set_cookie(
        key="access_token",
        value=new_access,
        httponly=True,
        secure=True,
        max_age=config.ACCESS_TOKEN_EXPIRE_TIME,
        samesite="strict",
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=True,
        max_age=config.REFRESH_TOKEN_EXPIRE_TIME,
        samesite="strict",
        path="/auth",
    )

    return response
```
---