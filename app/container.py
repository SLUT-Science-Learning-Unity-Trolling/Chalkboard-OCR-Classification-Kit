from punq import Container

from app.config import Config
from app.core.services.auth_service import AuthService
from app.core.services.security_service import SecurityService
from app.core.services.user_service import UserService
from app.adapters.gateways.mongo import MongoGateway
from app.adapters.repositories.mongo_repo import MongoRepo


def build_container() -> Container:
    """Билдер контейнера."""
    container = Container()

    container.register(MongoGateway, factory=lambda: MongoGateway())

    container.register(
        MongoRepo,
        factory=lambda: MongoRepo(
            gateway=container.resolve(MongoGateway),
            collection_name="users",
        ),
    )

    container.register(SecurityService, factory=lambda: SecurityService())

    container.register(
        UserService,
        factory=lambda: UserService(
            repository=container.resolve(MongoRepo),
            security=container.resolve(SecurityService),
        ),
    )

    container.register(
        AuthService,
        factory=lambda: AuthService(
            repository=container.resolve(MongoRepo),
            security=container.resolve(SecurityService),
        ),
    )

    container.register("config", instance=Config())

    return container
