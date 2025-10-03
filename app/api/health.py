from litestar import get
from litestar.status_codes import HTTP_200_OK


@get("/health", status_code=HTTP_200_OK)
async def health_check() -> dict:
    return {"status": "healthy"}
