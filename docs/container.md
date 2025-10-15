# Модуль container

Контейнер зависимостей.

## def build_container:
#### Регистрация зависимостей в контейнере.

```python
def build_container() -> Container:
    """Регистрация зависимостей в контейнере."""
    container = Container()

    """Mongo и child репозитории"""
    # MongoGateway
    container.register(MongoGateway, factory=lambda: MongoGateway())

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
        ),
    )

    """Регистрация конфига"""
    # Config
    container.register("config", instance=Config())

    return container
```
---