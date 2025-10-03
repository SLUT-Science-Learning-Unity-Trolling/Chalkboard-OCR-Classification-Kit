from litestar import Litestar
from litestar.openapi import OpenAPIConfig

from app.api.health import health_check
from app.api.user import auth_user, create_user
from app.container import build_container


openapi_config = OpenAPIConfig(
    title="COCK API",
    version="1.0.0",
    description="Chalkboard OCR Classification Kit API",
    enabled_endpoints=["swagger", "redoc", "elements", "openapi.json"],
)

app = Litestar(
    route_handlers=[create_user, health_check, auth_user],
    dependencies={"container": build_container},
    openapi_config=openapi_config,
    debug=True,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
