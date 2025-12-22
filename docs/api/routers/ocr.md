# Модуль ocr

Модуль содержит эндпоинты для работы с OCR функционалом.

## def ocr_to_pdf:
#### Маршруты:
- `@post( "/users/ocr/pdf", status_code=HTTP_201_CREATED, dependencies={"current_user": Provide(AuthService.get_current_user)}, )`

```python
@post(
    "/users/ocr/pdf",
    status_code=HTTP_201_CREATED,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def ocr_to_pdf(
    container: Container,
    current_user: UserDTO,  # <-- КЛЮЧЕВО: добавить аннотацию
    data: Annotated[UploadFile, Body(media_type=RequestEncodingType.MULTI_PART)],
) -> Response:
    image_bytes = await data.read()
    pdf_bytes = await asyncio.to_thread(image_bytes_to_pdf_bytes, image_bytes)

    out_name = (data.filename or "document").rsplit(".", 1)[0] + ".pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{out_name}"'},
    )
```
---