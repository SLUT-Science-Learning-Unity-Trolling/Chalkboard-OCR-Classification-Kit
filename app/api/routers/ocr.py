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
from app.core.services.ocr_service import images_bytes_to_pdf_bytes


@post(
    "/users/ocr/pdf",
    tags=["OCR"],
    status_code=HTTP_201_CREATED,
    dependencies={"current_user": Provide(AuthService.get_current_user)},
)
async def ocr_to_pdf(
    container: Container,
    current_user: UserDTO,
    data: Annotated[list[UploadFile], Body(media_type=RequestEncodingType.MULTI_PART)],
) -> Response:
    """
    Принимает несколько изображений и возвращает один PDF,
    где перед каждым блоком текста будет:
        Фото 1
        Фото 2
        ...
    """

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
