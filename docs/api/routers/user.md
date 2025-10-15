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
## def upload_image:
#### Эндпоинт загрузки локального изображения пользователя через UploadFile.
#### Маршруты:
- `@post( "/users/upload_image", status_code=HTTP_201_CREATED, return_dto=DataclassDTO[ImageDTO], dependencies={"current_user": Provide(AuthService.get_current_user)}, )`

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `container` | `Container` | Контейнер |
| `current_user` | `UserDTO` | Пользователь |
| `data` | `UploadFile` | Файл изображения |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `ImageDTO` | Данные изображения |

```python
@post(
    "/users/upload_image",
    status_code=HTTP_201_CREATED,
    return_dto=DataclassDTO[ImageDTO],
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def upload_image(
    container: Container,
    current_user: UserDTO,
    data: Annotated[UploadFile, Body(media_type=RequestEncodingType.MULTI_PART)],
) -> ImageDTO:
    """Эндпоинт загрузки локального изображения пользователя через UploadFile.

    Args:
        container (Container): Контейнер
        current_user (UserDTO): Пользователь
        data (UploadFile): Файл изображения

    Returns:
        ImageDTO: Данные изображения
    """
    user_service = container.resolve(UserService)
    try:
        user_id = current_user.id
    except AbsentUserError:
        raise AbsentUserError("Не выполнен вход в аккаунт") from None

    try:
        image: UploadedImage = await user_service.upload_image(
            user_id=user_id, file=data
        )

        image_dict = image.__dict__.copy()
        if "_id" in image_dict and isinstance(image_dict["_id"], ObjectId):
            image_dict["_id"] = str(image_dict["_id"])

        return ImageDTO.fromrow(image_dict)

    except (
        ImageExtensionValidationError,
        ImageUploadError,
    ) as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e)) from e
```
---
## def get_all_user_images:
#### Эндпоинт получения всех изображений пользователя.
#### Маршруты:
- `@get( "users/get_all_user_images", status_code=HTTP_201_CREATED, return_dto=DataclassDTO[ImageDTO], dependencies={"current_user": Provide(AuthService.get_current_user)}, )`

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `container` | `Container` | Контейнер |
| `current_user` | `UserDTO` | Пользователь |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `list[ImageDTO]` | Список изображений пользователя |

```python
@get(
    "users/get_all_user_images",
    status_code=HTTP_201_CREATED,
    return_dto=DataclassDTO[ImageDTO],
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def get_all_user_images(
    container: Container,
    current_user: UserDTO,
) -> list[ImageDTO]:
    """Эндпоинт получения всех изображений пользователя.

    Args:
        container (Container): Контейнер
        current_user (UserDTO): Пользователь

    Returns:
        list[ImageDTO]: Список изображений пользователя
    """
    user_service = container.resolve(UserService)
    try:
        user_id = current_user.id
    except AbsentUserError:
        raise AbsentUserError("Не выполнен вход в аккаунт") from None

    try:
        images: list[UploadedImage] = await user_service.get_all_user_images(
            user_id=user_id
        )
        return [ImageDTO.fromrow(image.__dict__) for image in images]

    except ImageUploadError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e)) from e
```
---
## def delete_image:
#### Эндпоинт удаления изображения пользователя.
#### Маршруты:
- `@delete( "users/delete_image", status_code=HTTP_200_OK, dependencies={"current_user": Provide(AuthService.get_current_user)}, )`

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `container` | `Container` | Контейнер |
| `current_user` | `UserDTO` | Пользователь |
| `url` | `str` | Путь к изображению |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `dict[str, str]` | Сообщение об успешном удалении изображения |

```python
@delete(
    "users/delete_image",
    status_code=HTTP_200_OK,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def delete_image(
    container: Container,
    current_user: UserDTO,
    url: str,
) -> dict[str, str]:
    """Эндпоинт удаления изображения пользователя.

    Args:
        container (Container): Контейнер
        current_user (UserDTO): Пользователь
        url (str): Путь к изображению

    Returns:
        dict[str, str]: Сообщение об успешном удалении изображения
    """
    user_service = container.resolve(UserService)

    try:
        user_id = current_user.id
    except AbsentUserError as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=f"Не выполнен вход в аккаунт: {e}"
        ) from e

    try:
        await user_service.delete_image(user_id=user_id, url=url)
        return {"success": "true", "message": "Изображение успешно удалено"}
    except DeleteImageError as e:
        return {"success": "false", "message": f"Ошибка при удалении изображения: {e}"}
    except Exception as e:
        return {"success": "false", "message": f"Произошла непредвиденная ошибка: {e}"}
```
---