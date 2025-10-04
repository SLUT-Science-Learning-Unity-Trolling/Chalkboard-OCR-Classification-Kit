from litestar import Litestar
from litestar.openapi import OpenAPIConfig

from app.api.health import db_health_check, server_health_check
from app.api.misc import get_me
from app.api.user import auth_user, create_user, logout_user
from app.container import build_container


openapi_config = OpenAPIConfig(
    title="COCK API",
    version="1.0.0",
    description="Chalkboard OCR Classification Kit API",
    enabled_endpoints=["swagger", "redoc", "elements", "openapi.json"],
)

app = Litestar(
    route_handlers=[
        server_health_check,
        db_health_check,
        create_user,
        auth_user,
        logout_user,
        get_me,
    ],
    dependencies={"container": build_container},
    openapi_config=openapi_config,
    debug=True,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
