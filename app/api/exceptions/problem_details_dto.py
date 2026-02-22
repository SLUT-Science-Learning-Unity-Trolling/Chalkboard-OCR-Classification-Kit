"""DTO для стандартизированного описания ошибок в формате RFC 7807."""

from dataclasses import dataclass


@dataclass(slots=True)
class ProblemDetailsDTO:
    """Data Transfer Object (DTO) для передачи деталей ошибки.

    Используется для унификации формата ошибок API в соответствии с
    спецификацией RFC 7807 (`application/problem+json`).

    Attributes:
        type (str): URI, идентифицирующий тип ошибки.
        title (str): Краткое описание ошибки, понятное для разработчиков и клиентов.
        status (int): HTTP-статус код ошибки.
        detail (str): Подробное сообщение об ошибке, раскрывающее причину её возникновения.
    """
    type: str
    title: str
    status: int
    detail: str