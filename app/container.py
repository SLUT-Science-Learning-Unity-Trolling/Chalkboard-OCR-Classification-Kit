from punq import Container
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from app.core.models.user import User
from app.core.services.user_service import UserService
from app.infrastructure.gateways.mongo import MongoGateway
from app.infrastructure.repositories.mongo_repo import MongoRepo
from app.schema.user_dto import UserDTO


async def user_endpoint(request):
    container = request.app.state.container
    user_service = container.resolve(UserService)
    user = await user_service.create_user("testuser", "test@example.com")
    return JSONResponse(
        {"id": str(user.id), "username": user.username, "email": user.email}
    )


def build_container() -> Container:
    container = Container()

    container.register(MongoGateway, instance=MongoGateway())

    container.register(
        MongoRepo,
        instance=MongoRepo(
            gateway=container.resolve(MongoGateway),
            collection_name="users",
            dto_model=UserDTO,
            to_domain=User,
        ),
    )

    container.register(
        UserService,
        factory=lambda: UserService(repository=container.resolve(MongoRepo)),
    )

    app = Starlette(
        debug=True,
        routes=[
            Route("/user", user_endpoint, methods=["POST"]),
        ],
    )
    app.state.container = container

    container.register(Starlette, instance=app)

    return container
