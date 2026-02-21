"""Контейнер зависимостей."""
# Container


from typing import Any

from punq import Container

from app.adapters.gateways.mongo import MongoGateway
from app.adapters.gateways.redis import RedisGateway
from app.adapters.gateways.s3 import MinioGateway
from app.adapters.repositories.image_repo import ImageRepo
from app.adapters.repositories.mongo_repo import MongoRepo
from app.adapters.repositories.redis_blacklist_repo import RedisBlacklistRepo
from app.adapters.repositories.redis_rate_limit_repo import RedisRateLimitRepo
from app.adapters.repositories.user_repo import UserRepo
from app.config import Config
from app.core.services.auth_service import AuthService
from app.core.services.security_service import SecurityService
from app.core.services.user_service import UserService
from app.core.services.validation_service import ValidationService
from app.monitoring.api_monitor import ApiMonitor


def build_container() -> Container:
    """Регистрация зависимостей в контейнере."""
    container = Container()

    def register_gateway_singleton(typ: type, factory: Any) -> None:
        """Функция для генерации одноэкземпляровых контейнеров."""
        container.register(typ, factory=factory, scope="singleton")

    register_gateway_singleton(MongoGateway, factory=lambda: MongoGateway())

    register_gateway_singleton(MinioGateway, factory=lambda: MinioGateway())

    def register_redis_pair(db_index: int, gateway_name_suffix: str, repo_cls: Any) -> None:
        """Регистрация 2 типов контейнеров редиса. Rate limit и Blacklist."""
        gateway_type = type(f"RedisGatewayDb{db_index}_{gateway_name_suffix}", (RedisGateway,), {})
        register_gateway_singleton(gateway_type, factory=lambda db=db_index: RedisGateway(db=db))
        container.register(
            repo_cls,
            factory=lambda gw_type=gateway_type: repo_cls(gateway=container.resolve(gw_type))
        )

    register_redis_pair(0, "blacklist", RedisBlacklistRepo)
    register_redis_pair(1, "ratelimit", RedisRateLimitRepo)

    def register_mongo_repo(interface: Any, collection_name: str) -> None:
        """Фабрика для регистрации монго контейнеров."""
        container.register(
            interface,
            factory=lambda coll=collection_name: MongoRepo(
                gateway=container.resolve(MongoGateway),
                collection_name=coll,
            ),
        )

    register_mongo_repo(UserRepo, "users")
    register_mongo_repo(ImageRepo, "images")

    container.register(SecurityService, factory=lambda: SecurityService(), scope="singleton")
    container.register(ValidationService, factory=lambda: ValidationService(), scope="singleton")

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

    container.register(
        AuthService,
        factory=lambda: AuthService(
            repository=container.resolve(UserRepo),
            security=container.resolve(SecurityService),
            validation=container.resolve(ValidationService),
            redis_blacklist_repo=container.resolve(RedisBlacklistRepo),
            redis_rate_limit_repo=container.resolve(RedisRateLimitRepo),
        ),
    )

    container.register("config", instance=Config())

    container.register(ApiMonitor, ApiMonitor, scope="singleton")

    return container
