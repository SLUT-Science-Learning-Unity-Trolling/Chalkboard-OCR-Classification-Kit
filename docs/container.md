# Модуль container

Модуль для построения и конфигурации контейнера зависимостей.

Контейнер позволяет централизованно управлять всеми сервисами, репозиториями
и шлюзами, используемыми в приложении, обеспечивая единый доступ к
одноэкземпляровым объектам и упрощая внедрение зависимостей.

## def build_container:
#### Создает и конфигурирует контейнер зависимостей.

Регистрация включает:
- Шлюзы (Mongo, Redis, Minio)
- Репозитории (UserRepo, ImageRepo, Redis Blacklist/RateLimit)
- Сервисы (AuthService, UserService, ValidationService, SecurityService)
- Конфигурацию приложения (Config)
- Монитор API (ApiMonitor)

Используется паттерн singleton для одноэкземпляровых объектов, таких как
шлюзы и сервисы.

#### Возвращает
| Тип | Описание |
|-----|----------|
| `Container` | Полностью настроенный контейнер зависимостей. |

```python
def build_container() -> Container:
    """Создает и конфигурирует контейнер зависимостей.

    Регистрация включает:
        - Шлюзы (Mongo, Redis, Minio)
        - Репозитории (UserRepo, ImageRepo, Redis Blacklist/RateLimit)
        - Сервисы (AuthService, UserService, ValidationService, SecurityService)
        - Конфигурацию приложения (Config)
        - Монитор API (ApiMonitor)

    Используется паттерн singleton для одноэкземпляровых объектов, таких как
    шлюзы и сервисы.

    Returns:
        Container: Полностью настроенный контейнер зависимостей.
    """
    container = Container()

    def register_gateway_singleton(typ: type, factory: Any) -> None:
        """Регистрирует шлюз как одноэкземпляровый объект в контейнере.

        Args:
            typ (type): Класс шлюза
            factory (Any): Функция для создания экземпляра шлюза
        """
        container.register(typ, factory=factory, scope="singleton")

    register_gateway_singleton(MongoGateway, factory=lambda: MongoGateway())

    register_gateway_singleton(MinioGateway, factory=lambda: MinioGateway())

    def register_redis_pair(db_index: int, gateway_name_suffix: str, repo_cls: Any) -> None:
        """Регистрация пары Redis: шлюз + репозиторий.

        Позволяет разделять БД Redis для разных целей (черный список токенов и
        rate limiting).

        Args:
            db_index (int): Индекс базы данных Redis
            gateway_name_suffix (str): Суффикс для создания уникального класса шлюза
            repo_cls (Any): Класс репозитория, который использует этот шлюз
        """
        gateway_type = type(f"RedisGatewayDb{db_index}_{gateway_name_suffix}", (RedisGateway,), {})
        register_gateway_singleton(gateway_type, factory=lambda db=db_index: RedisGateway(db=db))
        container.register(
            repo_cls,
            factory=lambda gw_type=gateway_type: repo_cls(gateway=container.resolve(gw_type))
        )

    register_redis_pair(0, "blacklist", RedisBlacklistRepo)
    register_redis_pair(1, "ratelimit", RedisRateLimitRepo)

    def register_mongo_repo(interface: Any, collection_name: str) -> None:
        """Регистрация Mongo репозитория с указанной коллекцией.

        Args:
            interface (Any): Интерфейс репозитория
            collection_name (str): Имя коллекции в MongoDB
        """
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
```
---