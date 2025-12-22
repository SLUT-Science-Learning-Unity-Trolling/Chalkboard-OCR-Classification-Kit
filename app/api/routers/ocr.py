"""Модуль содержит эндпоинты для работы с OCR функционалом."""

import asyncio
from typing import Annotated

from litestar import Response, post
from litestar.datastructures import UploadFile
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.status_codes import HTTP_201_CREATED
from punq import Container

from app.api.schemas.user_dto import UserDTO
from app.core.services.auth_service import AuthService
from app.core.services.ocr_service import image_bytes_to_pdf_bytes


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
