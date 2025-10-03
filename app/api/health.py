from litestar import get
from litestar.status_codes import HTTP_200_OK
from starlette.responses import JSONResponse


@get("/health", status_code=HTTP_200_OK)
def health_check() -> JSONResponse:
    """Проверка работы сервера."""
    return JSONResponse({"status": "ok"})
