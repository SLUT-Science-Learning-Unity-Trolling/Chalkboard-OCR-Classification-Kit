# Модуль api_monitoring

Middleware для мониторинга API.

## def api_monitor_middleware:
#### Фабрика ASGI middleware для мониторинга API.

Извлекает `ApiMonitor` из DI-контейнера, если он есть, иначе создаёт новый.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `container` | `Container` | DI-контейнер с сервисами приложения. |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `Callable[[ASGIApp], ASGIApp]` | Функция, которая принимает ASGI-приложение и возвращает новое приложение с middleware мониторинга. |

```python
def api_monitor_middleware(container: Container) -> Callable[[ASGIApp], ASGIApp]:
    """Фабрика ASGI middleware для мониторинга API.

    Извлекает `ApiMonitor` из DI-контейнера, если он есть, иначе создаёт новый.

    Args:
        container (Container): DI-контейнер с сервисами приложения.

    Returns:
        Callable[[ASGIApp], ASGIApp]: Функция, которая принимает ASGI-приложение и возвращает новое приложение с middleware мониторинга.
    """

    def create_middleware(app: ASGIApp) -> ASGIApp:
        monitor: ApiMonitor
        try:
            monitor = container.resolve(ApiMonitor)
        except Exception:
            monitor = ApiMonitor()

        async def middleware(scope: Scope, receive: Receive, send: Send) -> None:
            """Создаёт middleware для счётчика запросов.

            Оборачивает приложение и выполняет:
                - Измерение времени выполнения запроса.
                - Перехват кода ответа через send wrapper.
                - Передачу данных в ApiMonitor.

            Args:
                app (ASGIApp): ASGI-приложение для обёртывания.
                scope (Scope): Скоуп запроса.
                receive (Receive): Функция для получения сообщений.
                send (Send): Функция для отправки сообщений.

            Returns:
                ASGIApp: Обёрнутое приложение с мониторингом.
            """
            if scope["type"] != "http":
                await app(scope, receive, send)
                return

            path = scope.get("path", "")
            method = scope.get("method", "UNKNOWN")

            start = perf_counter()
            status_code = 500

            async def send_wrapper(message: dict) -> None:
                """Wrapper для перехвата статуса HTTP-ответа.

                Args:
                    message (dict): ASGI-сообщение.
                """
                nonlocal status_code
                if message.get("type") == "http.response.start":
                    status = message.get("status")
                    if isinstance(status, int):
                        status_code = status
                await send(message)

            await app(scope, receive, send_wrapper)
            latency_ms = (perf_counter() - start) * 1000.0
            monitor.record(path, method, status_code, latency_ms)

        return middleware

    return create_middleware
```
---