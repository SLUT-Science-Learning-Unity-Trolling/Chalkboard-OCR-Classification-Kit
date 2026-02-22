"""Модуль содержит эндпоинты для работы с OCR функционалом."""

import asyncio

from typing import Annotated

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
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from punq import Container

from app.api.exceptions.problem_details_dto import ProblemDetailsDTO
from app.api.exceptions.problem_factory import ErrorCodes
from app.api.schemas.user_dto import UserDTO
from app.core.services.auth_service import AuthService
from app.core.services.ocr_service import images_bytes_to_pdf_bytes


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


ocr_router = Router(path="/users/ocr", tags=["OCR"], route_handlers=[ocr_to_pdf])
