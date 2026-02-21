# Модуль ocr

Модуль содержит эндпоинты для работы с OCR функционалом.

## def ocr_to_pdf:
#### Принимает несколько изображений и возвращает один PDF, где перед каждым блоком текста будет: [Фото 1, Фото 2, ...].
#### Маршруты:
- `@post( "/pdf", tags=["OCR"], status_code=HTTP_200_OK, dependencies={"current_user": Provide(AuthService.get_current_user)}, responses={ HTTP_200_OK: ResponseSpec( description="Файл успешно обработан и возвращен в виде PDF", data_container=None, ), HTTP_401_UNAUTHORIZED: ResponseSpec( description="Пользователь не авторизован", data_container=ProblemDetailsDTO, examples=[ Example( value=ErrorCodes.AUTHENTICATION_ERROR.example( "Пользователь не авторизован или сессия истекла" ), )`

```python
@post(
    "/pdf",
    tags=["OCR"],
    status_code=HTTP_200_OK,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
    responses={
        HTTP_200_OK: ResponseSpec(
            description="Файл успешно обработан и возвращен в виде PDF",
            data_container=None,
        ),
        HTTP_401_UNAUTHORIZED: ResponseSpec(
            description="Пользователь не авторизован",
            data_container=ProblemDetailsDTO,
            examples=[
                Example(
                    value=ErrorCodes.AUTHENTICATION_ERROR.example(
                        "Пользователь не авторизован или сессия истекла"
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
async def ocr_to_pdf(
    container: Container,
    current_user: UserDTO,
    data: Annotated[list[UploadFile], Body(media_type=RequestEncodingType.MULTI_PART)],
) -> Response:
    """Принимает несколько изображений и возвращает один PDF, где перед каждым блоком текста будет: [Фото 1, Фото 2, ...]."""
    images_bytes: list[bytes] = []

    for file in data:
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