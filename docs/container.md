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
        container.register(typ, factory=factory, scope=Scope.singleton)

    register_gateway_singleton(MongoGateway, factory=lambda: MongoGateway())

    register_gateway_singleton(MinioGateway, factory=lambda: MinioGateway())

    def register_redis_pair(
        db_index: int, gateway_name_suffix: str, repo_cls: Any
    ) -> None:
        """Регистрация пары Redis: шлюз + репозиторий.

        Позволяет разделять БД Redis для разных целей (черный список токенов и
        rate limiting).

        Args:
            db_index (int): Индекс базы данных Redis
            gateway_name_suffix (str): Суффикс для создания уникального класса шлюза
            repo_cls (Any): Класс репозитория, который использует этот шлюз
        """
        gateway_type = type(
            f"RedisGatewayDb{db_index}_{gateway_name_suffix}", (RedisGateway,), {}
        )
        register_gateway_singleton(
            gateway_type, factory=lambda db=db_index: RedisGateway(db=db)
        )
        container.register(
            repo_cls,
            factory=lambda gw_type=gateway_type: repo_cls(
                gateway=container.resolve(gw_type)
            ),
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
                gateway=container.resolve(MongoGateway),  # type: ignore
                collection_name=coll,
            ),
        )

    register_mongo_repo(UserRepo, "users")
    register_mongo_repo(ImageRepo, "images")

    container.register(SecurityService, SecurityService, scope=Scope.singleton)
    container.register(ValidationService, ValidationService, scope=Scope.singleton)
    container.register(ImageValidator, ImageValidator, scope=Scope.singleton)

    container.register(
        UserService,
        factory=lambda: UserService(
            user_repo=container.resolve(UserRepo),  # type: ignore
            image_repo=container.resolve(ImageRepo),  # type: ignore
            security=container.resolve(SecurityService),  # type: ignore
            validator=container.resolve(ValidationService),  # type: ignore
            image_validator=container.resolve(ImageValidator),  # type: ignore
            storage=container.resolve(MinioGateway),  # type: ignore
        ),
    )

    container.register(
        AuthService,
        factory=lambda: AuthService(
            repository=container.resolve(UserRepo),  # type: ignore
            security=container.resolve(SecurityService),  # type: ignore
            validation=container.resolve(ValidationService),  # type: ignore
            redis_blacklist_repo=container.resolve(RedisBlacklistRepo),  # type: ignore
            redis_rate_limit_repo=container.resolve(RedisRateLimitRepo),  # type: ignore
        ),
    )

    container.register(Config, instance=Config())

    container.register(ApiMonitor, ApiMonitor, scope=Scope.singleton)

    def register_ocr_engines(container: Container, device: str = "cpu") -> None:
        """Регистрация OCR движков в контейнере."""
        
        # Формула/распознавание формул
        container.register(
            Pix2TextEngine,
            factory=lambda: Pix2TextEngine.from_config(device=device),
            scope=Scope.singleton,
        )

        # Текстовый OCR (PaddleOCR)
        container.register(
            PaddleOCREngine,
            factory=lambda: PaddleOCREngine.from_config(device=device),
            scope=Scope.singleton,
        )

        # Текстовый OCR (Tesseract)
        container.register(
            TesseractOCREngine,
            factory=lambda: TesseractOCREngine.from_config(),
            scope=Scope.singleton,
        )

        # Текстовый OCR (EasyOCR)
        container.register(
            EasyOCREngine,
            factory=lambda: EasyOCREngine.from_config(lang=["ru"], gpu=False),
            scope=Scope.singleton,
        )

        # Текстовый OCR (RapidOCR)
        container.register(
            RapidOCREngine,
            factory=lambda: RapidOCREngine.from_config(),
            scope=Scope.singleton,
        )

        # Текстовый OCR (Doctr)
        container.register(
            DocTROCREngine,
            factory=lambda: DocTROCREngine.from_config(),
            scope=Scope.singleton,
        )

    register_ocr_engines(container, device="cpu")

    container.register(
        OCRService,
        factory=lambda: OCRService(
            formula_engine=container.resolve(Pix2TextEngine),
            text_engine=container.resolve(PaddleOCREngine),
        ),
        scope=Scope.singleton,
    )

    return container
```
---