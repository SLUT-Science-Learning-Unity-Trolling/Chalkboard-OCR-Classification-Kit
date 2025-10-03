from litestar import Litestar
from litestar.di import Provide
from litestar.openapi import OpenAPIConfig

from app.api.health import health_check
from app.api.user import create_user
from app.container import build_container
from app.core.services.user_service import UserService


async def provide_user_service() -> UserService:
    container = build_container()
    return container.resolve(UserService)


openapi_config = OpenAPIConfig(
    title="COCK API",
    version="1.0.0",
    description="Chalkboard OCR Classification Kit API",
    enabled_endpoints=["swagger", "redoc", "openapi.json"],
)

app = Litestar(
    route_handlers=[create_user, health_check],
    dependencies={"user_service": Provide(provide_user_service)},
    openapi_config=openapi_config,
    debug=True,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
