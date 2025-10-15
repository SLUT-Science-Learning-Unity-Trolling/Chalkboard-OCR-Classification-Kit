# Модуль container

Контейнер зависимостей.

## def build_container:
#### Билдер контейнера.

```python
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

    container.register(
        MinioGateway,
        factory=lambda: MinioGateway(),
    )

    container.register(SecurityService, factory=lambda: SecurityService())
    container.register(ValidationService, factory=lambda: ValidationService())

    container.register(
        UserService,
        factory=lambda: UserService(
            repository=container.resolve(MongoRepo),
            security=container.resolve(SecurityService),
            validator=container.resolve(ValidationService),
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
```
---