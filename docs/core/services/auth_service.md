# Модуль auth_service

Модуль содержит класс AuthService для аутентификации пользователей.

## Класс AuthService

**Сервис для аутентификации пользователей.**

Методы класса обеспечивают:
    - Авторизацию существующих пользователей.
    - Получение текущего пользователя по access_token.
    - Перевыпуск access и refresh токенов.
    - Добавление токенов в черный список.

```python
class AuthService:
    """Сервис для аутентификации пользователей.

    Методы класса обеспечивают:
        - Авторизацию существующих пользователей.
        - Получение текущего пользователя по access_token.
        - Перевыпуск access и refresh токенов.
        - Добавление токенов в черный список.
    """
```

---
## def init:
#### Инициализация сервиса аутентификации.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `repository` | `RepositoryInterface` | Репозиторий пользователей. |
| `security` | `SecurityService` | Сервис для работы с хэшированием паролей. |
| `validation` | `ValidationService` | Сервис для валидации |
| `redis_blacklist_repo` | `RedisBlacklistRepo` | Репозиторий для черного списка токенов. |
| `redis_rate_limit_repo` | `RedisRateLimitRepo` | Репозиторий для хранения данных о rate limit. |

```python
    def __init__(
        self,
        repository: RepositoryInterface,
        security: SecurityService,
        validation: ValidationService,
        redis_blacklist_repo: RedisBlacklistRepo,
        redis_rate_limit_repo: RedisRateLimitRepo,
    ) -> None:
        """Инициализация сервиса аутентификации.

        Args:
            repository (RepositoryInterface): Репозиторий пользователей.
            security (SecurityService): Сервис для работы с хэшированием паролей.
            validation (ValidationService): Сервис для валидации
            redis_blacklist_repo (RedisBlacklistRepo): Репозиторий для черного списка токенов.
            redis_rate_limit_repo (RedisRateLimitRepo): Репозиторий для хранения данных о rate limit.
        """
        self._repo = repository
        self._security = security
        self._validation = validation
        self._redis_blacklist = redis_blacklist_repo
        self._redis_rate_limit = redis_rate_limit_repo
```
---
## async def auth_existing_user:
#### Аутентификация существующего пользователя по email или username.

Проверяет существование пользователя, валидирует пароль и
генерирует JWT-токен для авторизации.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `identifier` | `str` | Email или имя пользователя (username). |
| `password` | `str` | Пароль пользователя. |
| `client_ip` | `str` | IP-адрес клиента для проверки rate limit. |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `tuple[UserDTO, str, str]` | DTO пользователя и JWT-токен. |

#### Исключения
| Исключение | Описание |
|------------|----------|
| `InvalidEmailOrPassword` | Если пользователь не найден или пароль неверный. |

```python
    async def auth_existing_user(
        self, identifier: str, password: str, client_ip: str
    ) -> tuple[UserDTO, str, str]:
        """Аутентификация существующего пользователя по email или username.

        Проверяет существование пользователя, валидирует пароль и
        генерирует JWT-токен для авторизации.

        Args:
            identifier (str): Email или имя пользователя (username).
            password (str): Пароль пользователя.
            client_ip (str): IP-адрес клиента для проверки rate limit.

        Raises:
            InvalidEmailOrPassword: Если пользователь не найден или пароль неверный.

        Returns:
            tuple[UserDTO, str, str]: DTO пользователя и JWT-токен.
        """
        is_email: bool = "@" in identifier

        if is_email:
            self._validation.validate_credentials(
                identifier=identifier,
                password=password,
                is_email=True,
            )
            query: dict[str, str] = {"email": identifier}
        else:
            self._validation.validate_credentials(
                identifier=identifier, password=password, is_email=False
            )
            query: dict[str, str] = {"username": identifier}

        user = await self._repo.get_one(query)
        if not user:
            raise InvalidEmailOrPasswordError

        hash, salt = self._security.deserialize_hash(user["password_hash"])
        if not self._security.verify_hash(password=password, salt=salt, hash_=hash):
            raise InvalidEmailOrPasswordError

        access_token: str = paseto.create(
            key=token_key,
            purpose="local",
            claims={
                "sub": str(user["_id"]),
                "username": user["username"],
                "email": user["email"],
                "type": "access",
                "jti": secrets.token_hex(8),
            },
            exp_seconds=config.ACCESS_TOKEN_EXPIRE_TIME,
        )

        refresh_token: str = paseto.create(
            key=token_key,
            purpose="local",
            claims={
                "sub": str(user["_id"]),
                "type": "refresh",
                "jti": secrets.token_hex(16),
            },
            exp_seconds=config.REFRESH_TOKEN_EXPIRE_TIME,
        )

        user_dto: UserDTO = UserDTO(
            id=str(user["_id"]),
            username=user["username"],
            email=user["email"],
        )

        return user_dto, access_token, refresh_token
```
---
## def get_current_user:
#### Возвращает текущего авторизованного пользователя.

Проверяет JWT-токен в cookies запроса, извлекает пользователя из базы
через UserService и возвращает его DTO.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `request` | `Request` | HTTP-запрос. |
| `container` | `Container` | Контейнер зависимостей для получения сервисов. |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `Optional[UserDTO]` | DTO текущего пользователя или None, если пользователь не авторизован. |

```python
    @staticmethod
    async def get_current_user(
        request: Request, container: Container
    ) -> UserDTO | None:
        """Возвращает текущего авторизованного пользователя.

        Проверяет JWT-токен в cookies запроса, извлекает пользователя из базы
        через UserService и возвращает его DTO.

        Args:
            request (Request): HTTP-запрос.
            container (Container): Контейнер зависимостей для получения сервисов.

        Returns:
            Optional[UserDTO]: DTO текущего пользователя или None, если пользователь не авторизован.
        """
        token = request.cookies.get("access_token")
        if not token:
            raise UnauthorizedError("Пользователь не авторизован или сессия истекла")

        try:
            parsed = paseto.parse(
                key=token_key,
                purpose="local",
                token=token,
            )

            claims = parsed["message"]

            if claims.get("type") != "access":
                raise InvalidTokenError("Неверный тип токена")

            user_id = claims["sub"]
            if not user_id:
                raise InvalidTokenError(
                    "В токене отсутствует идентификатор пользователя."
                )

        except Exception:
            raise InvalidTokenError("Невалидный токен") from None

        user_service = container.resolve(UserService)
        user = await user_service.get_user_by_id(user_id)

        if not user:
            raise UnauthorizedError("Пользователь не найден в базе данных.")

        return UserDTO.fromrow(user)
```
---
## async def refresh_tokens:
#### Перевыпуск access и refresh токенов по валидному refresh_token.

Проверяет черный список токенов и валидность PASETO.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `refresh_token` | `str` | Токен для обновления access токена. |
| `access_token` | `Optional[str]` | Существующий access_token (если есть). |
| `client_ip` | `str` | IP-адрес клиента для проверки лимита. |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `tuple[str, str]` | Новый access_token и refresh_token. |

#### Исключения
| Исключение | Описание |
|------------|----------|
| `UnauthorizedError` | Если токен невалиден или в черном списке. |

```python
    async def refresh_tokens(
        self, refresh_token: str, access_token: str | None, client_ip: str
    ) -> tuple[str, str]:
        """Перевыпуск access и refresh токенов по валидному refresh_token.

        Проверяет черный список токенов и валидность PASETO.

        Args:
            refresh_token (str): Токен для обновления access токена.
            access_token (Optional[str]): Существующий access_token (если есть).
            client_ip (str): IP-адрес клиента для проверки лимита.

        Raises:
            UnauthorizedError: Если токен невалиден или в черном списке.

        Returns:
            tuple[str, str]: Новый access_token и refresh_token.
        """
        if not refresh_token:
            raise UnauthorizedError("Пользователь не авторизован")

        def _parse_paseto(token: str, expected_type: str) -> dict[str, str]:
            """Парсинг PASETO и проверка типа токена."""
            try:
                parsed = paseto.parse(key=token_key, purpose="local", token=token)
                claims = parsed["message"]
            except Exception:
                raise UnauthorizedError(f"Неизвестный {expected_type} токен") from None

            if claims.get("type") != expected_type:
                raise UnauthorizedError(
                    f"Тип токена не соответствует {expected_type}"
                ) from None

            jti = claims.get("jti")
            if not jti:
                raise UnauthorizedError(
                    f"{expected_type.capitalize()} в токене отсутствует jti"
                ) from None

            return claims

        claims_refresh = _parse_paseto(refresh_token, "refresh")
        refresh_jti = claims_refresh["jti"]

        if self._redis_blacklist and await self._redis_blacklist.is_blacklisted(
            refresh_jti
        ):
            raise UnauthorizedError("Refresh токен в чёрном списке")

        user_id = claims_refresh["sub"]

        claims_access = None
        access_jti = None
        if access_token:
            claims_access = _parse_paseto(access_token, "access")
            access_jti = claims_access["jti"]
            if self._redis_blacklist and await self._redis_blacklist.is_blacklisted(
                access_jti
            ):
                raise UnauthorizedError("Access токен в чёрном списке")

        new_access = paseto.create(
            key=token_key,
            purpose="local",
            claims={
                "sub": user_id,
                "type": "access",
                "jti": secrets.token_hex(8),
            },
            exp_seconds=config.ACCESS_TOKEN_EXPIRE_TIME,
        )

        new_refresh = paseto.create(
            key=token_key,
            purpose="local",
            claims={
                "sub": user_id,
                "type": "refresh",
                "jti": secrets.token_hex(16),
            },
            exp_seconds=config.REFRESH_TOKEN_EXPIRE_TIME,
        )

        if self._redis_blacklist:
            await self._redis_blacklist.add_to_blacklist(
                refresh_jti, expires_in=config.REFRESH_TOKEN_EXPIRE_TIME
            )
            if access_jti:
                await self._redis_blacklist.add_to_blacklist(
                    access_jti, expires_in=config.ACCESS_TOKEN_EXPIRE_TIME
                )

        return new_access, new_refresh
```
---
## async def _blacklist_token:
#### Добавляет PASETO токен в черный список по jti.

Проверяет тип токена и сохраняет jti в RedisBlacklistRepo.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `token` | `str` | PASETO токен для добавления в blacklist. |
| `expected_type` | `str` | Ожидаемый тип токена ("access" или "refresh"). |
| `expires_in` | `int` | Время жизни токена в секундах. |

#### Исключения
| Исключение | Описание |
|------------|----------|
| `InvalidTokenError` | Если токен недействителен или тип не совпадает. |

```python
    async def _blacklist_token(
        self, token: str, expected_type: str, expires_in: int
    ) -> None:
        """Добавляет PASETO токен в черный список по jti.

        Проверяет тип токена и сохраняет jti в RedisBlacklistRepo.

        Args:
            token (str): PASETO токен для добавления в blacklist.
            expected_type (str): Ожидаемый тип токена ("access" или "refresh").
            expires_in (int): Время жизни токена в секундах.

        Raises:
            InvalidTokenError: Если токен недействителен или тип не совпадает.
        """
        try:
            parsed = paseto.parse(key=token_key, purpose="local", token=token)
            claims = parsed["message"]

            if claims.get("type") == expected_type:
                jti = claims.get("jti")
                if jti and self._redis_blacklist:
                    await self._redis_blacklist.add_to_blacklist(
                        jti, expires_in=expires_in
                    )
        except Exception:
            raise InvalidTokenError("Refresh токен не валиден") from None
```
---