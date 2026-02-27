# Модуль ocr

Модуль содержит эндпоинты для работы с OCR функционалом.

## def ocr_to_pdf:
#### Эндпоинт преобразования изображений в PDF.

Принимает список изображений и формирует единый PDF-файл
#### Маршрут:
- **Декоратор:** @post
- **Маршрут:** `/pdf`
- **Теги:** OCR


#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `container` | `Container` | DI-контейнер для получения сервисов. |
| `current_user` | `UserDTO` | Текущий авторизованный пользователь. |
| `data` | `list[UploadFile]` | Список загруженных файлов (изображений). |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `Response` | PDF-файл с объединёнными изображениями. |

```python
@post(
    "/pdf",
    tags=["OCR"],
    status_code=HTTP_200_OK,
    dependencies={
        "current_user": Provide(AuthService.get_current_user),
        "image_validator": Provide(ImageValidator),
    },
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Файл успешно обработан и возвращен в виде PDF",
            data_container=None,
        ),
        HTTP_401_UNAUTHORIZED: ResponseSpec(
            description="Пользователь не авторизован",
            data_container=ErrorMeta,
            examples=[
                Example(
                    value=problem_factory.build(
                        error=ErrorCode.AUTHENTICATION_ERROR,
                        detail="Пользователь не авторизован или сессия истекла",
                    ),
                )
            ],
        ),
        HTTP_500_INTERNAL_SERVER_ERROR: ResponseSpec(
            description="Внутренняя ошибка сервера",
            data_container=ErrorMeta,
            examples=[
                Example(
                    value=problem_factory.build(
                        error=ErrorCode.SERVICE_CONNECTION_ERROR,
                        detail="Внутренняя ошибка сервера",
                    ),
                )
            ],
        ),
        HTTP_429_TOO_MANY_REQUESTS: ResponseSpec(
            description="Слишком много запросов",
            data_container=ErrorMeta,
            examples=[
                Example(
                    value=problem_factory.build(
                        error=ErrorCode.TOO_MANY_REQUESTS,
                        detail="Слишком много попыток авторизации. Попробуйте позже.",
                    ),
                )
            ],
        ),
        HTTP_415_UNSUPPORTED_MEDIA_TYPE: ResponseSpec(
            description="Неподдерживаемый формат изображения",
            data_container=ErrorMeta,
            examples=[
                Example(
                    value=problem_factory.build(
                        error=ErrorCode.UNSUPPORTED_MEDIA_TYPE,
                        detail="Неподдерживаемый формат изображения",
                    )
                )
            ],
        ),
    },
)
async def ocr_to_pdf(
    container: Container,
    current_user: UserDTO,
    data: Annotated[list[UploadFile], Body(media_type=RequestEncodingType.MULTI_PART)],
) -> Response:
    """Эндпоинт преобразования изображений в PDF.

    Принимает список изображений и формирует единый PDF-файл

    Args:
        container (Container): DI-контейнер для получения сервисов.
        current_user (UserDTO): Текущий авторизованный пользователь.
        data (list[UploadFile]): Список загруженных файлов (изображений).

    Returns:
        Response: PDF-файл с объединёнными изображениями.
    """
    images_bytes: list[bytes] = []
    images_validator = container.resolve(ImageValidator)

    for file in data:
        images_validator.validate_image_file(file)
        images_bytes.append(await file.read())

    pdf_bytes = await asyncio.to_thread(
        images_bytes_to_pdf_bytes,
        images_bytes,
    )

    out_name = "document.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{out_name}"'},
    )
```
---