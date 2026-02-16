"""Контейнер зависимостей."""
# Container

from punq import Container

from app.adapters.gateways.mongo import MongoGateway
from app.adapters.gateways.redis import RedisGateway
from app.adapters.gateways.s3 import MinioGateway
from app.adapters.repositories.image_repo import ImageRepo
from app.adapters.repositories.mongo_repo import MongoRepo
from app.adapters.repositories.redis_repo import RedisRepo
from app.adapters.repositories.user_repo import UserRepo
from app.config import Config
from app.core.services.auth_service import AuthService
from app.core.services.security_service import SecurityService
from app.core.services.user_service import UserService
from app.core.services.validation_service import ValidationService


def build_container() -> Container:
    """Регистрация зависимостей в контейнере."""
    container = Container()

    """Mongo и child репозитории"""
    # MongoGateway
    container.register(MongoGateway, factory=lambda: MongoGateway())
    
    #Redis
    container.register(RedisGateway, factory=lambda: RedisGateway())
    container.register(
        RedisRepo,
        factory=lambda: RedisRepo(
            gateway=container.resolve(RedisGateway)
        ),
    )

    # UserRepo
    container.register(
        UserRepo,
        factory=lambda: MongoRepo(
            gateway=container.resolve(MongoGateway),
            collection_name="users",
        ),
    )

    # ImageRepo
    container.register(
        ImageRepo,
        factory=lambda: MongoRepo(
            gateway=container.resolve(MongoGateway),
            collection_name="images",
        ),
    )

    """Регистрация MiniO гейтвея"""
    # MinioGateway
    container.register(
        MinioGateway,
        factory=lambda: MinioGateway(),
    )

    """Регистрация сервисов"""
    # Security
    container.register(SecurityService, factory=lambda: SecurityService())

    # Validation
    container.register(ValidationService, factory=lambda: ValidationService())

    # User
    container.register(
        UserService,
        factory=lambda: UserService(
            user_repo=container.resolve(UserRepo),
            image_repo=container.resolve(ImageRepo),
            security=container.resolve(SecurityService),
            validator=container.resolve(ValidationService),
            storage=container.resolve(MinioGateway),
        ),
    )

    # Auth
    container.register(
        AuthService,
        factory=lambda: AuthService(
            repository=container.resolve(UserRepo),
            security=container.resolve(SecurityService),
            redis_repo=container.resolve(RedisRepo),
        ),
    )

    """Регистрация конфига"""
    # Config
    container.register("config", instance=Config())

    return container
