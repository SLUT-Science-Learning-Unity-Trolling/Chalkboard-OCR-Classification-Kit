# Модуль ocr

OCR endpoints.

## def ocr_to_pdf:
#### Преобразование списка изображений в единый PDF.
#### Маршрут:
- **Декоратор:** @post
- **Маршрут:** `/pdf`
- **Теги:** OCR


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
        HTTP_429_TOO_MANY_REQUESTS: ResponseSpec(
            description="Слишком много запросов",
            data_container=ErrorMeta,
        ),
        HTTP_500_INTERNAL_SERVER_ERROR: ResponseSpec(
            description="Внутренняя ошибка сервера",
            data_container=ErrorMeta,
        ),
    },
)
async def ocr_to_pdf(
    current_user: UserDTO,
    container: Container,
    data: Annotated[list[UploadFile], Body(media_type=RequestEncodingType.MULTI_PART)],
) -> Response:
    """Преобразование списка изображений в единый PDF."""
    
    ocr_service = container.resolve(OCRService)
    image_validator = container.resolve(ImageValidator)

    if not data:
        raise ValueError("No images provided")

    images_bytes: list[bytes] = []
    for file in data:
        image_validator.validate_image_file(file)
        images_bytes.append(await file.read())

    pdf_bytes = await asyncio.to_thread(ocr_service.images_bytes_to_pdf_bytes, images_bytes)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="document.pdf"'},
    )
```
---