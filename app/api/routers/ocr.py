"""OCR endpoints."""

import asyncio
from typing import Annotated
from punq import Container


from litestar import Response, Router, post
from litestar.datastructures import UploadFile
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.openapi import ResponseSpec
from litestar.openapi.spec import Example
from litestar.params import Body
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from app.api.exceptions.problem_factory import ErrorCode, ErrorMeta, problem_factory
from app.api.schemas.user_dto import UserDTO
from app.core.services import ocr_service
from app.core.services.auth_service import AuthService
from app.core.services.ocr_service import OCRService
from app.core.services.validation_service import ImageValidator


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


ocr_router = Router(
    path="/users/ocr",
    tags=["OCR"],
    route_handlers=[ocr_to_pdf],
)