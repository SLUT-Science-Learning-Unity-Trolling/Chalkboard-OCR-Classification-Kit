# Модуль api_monitor

Функция для мониторинга скорости API.

## Класс ApiMonitor

**Простой монитор API запросов с логированием в файл.**

Позволяет:
    - Считать общее количество запросов.
    - Собирать статистику по пути запроса, HTTP-методу и статусу ответа.
    - Хранить замеры времени обработки (latency) по каждому пути.
    - Выводить подробный лог в файл и на консоль в режиме отладки.

```python
class ApiMonitor:
    """Простой монитор API запросов с логированием в файл.

    Позволяет:

        - Считать общее количество запросов.
        - Собирать статистику по пути запроса, HTTP-методу и статусу ответа.
        - Хранить замеры времени обработки (latency) по каждому пути.
        - Выводить подробный лог в файл и на консоль в режиме отладки.
    """
```

---
## def init:
#### Инициализация ApiMonitor.

Создает лок, счетчики и структуры для хранения статистики.

```python
    def __init__(self) -> None:
        """Инициализация ApiMonitor.

        Создает лок, счетчики и структуры для хранения статистики.
        """
        self._lock = threading.Lock()
        self.total_requests = 0
        self.by_path: Counter[str] = Counter()
        self.by_method: Counter[str] = Counter()
        self.by_status: Counter[int] = Counter()
        self.latencies: defaultdict[str, list[float]] = defaultdict(list)
        self.debug = bool(config.DEBUG)
```
---
## def record:
#### Регистрирует один API-запрос.

Обновляет счетчики и замеры latency, логирует информацию о запросе.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `path` | `str` | URL путь запроса (например, "/auth/login") |
| `method` | `str` | HTTP-метод запроса ("GET", "POST", и т.д.) |
| `status` | `int` | HTTP статус ответа (например, 200, 401, 500) |
| `latency_ms` | `float` | Время обработки запроса в миллисекундах |

```python
    def record(self, path: str, method: str, status: int, latency_ms: float) -> None:
        """Регистрирует один API-запрос.

        Обновляет счетчики и замеры latency, логирует информацию о запросе.

        Args:
            path (str): URL путь запроса (например, "/auth/login")
            method (str): HTTP-метод запроса ("GET", "POST", и т.д.)
            status (int): HTTP статус ответа (например, 200, 401, 500)
            latency_ms (float): Время обработки запроса в миллисекундах
        """
        with self._lock:
            self.total_requests += 1
            self.by_path[path] += 1
            self.by_method[method] += 1
            self.by_status[status] += 1
            self.latencies[path].append(latency_ms)

        msg = f"{method} {path} - {status} -> {latency_ms:.1f} ms (total={self.total_requests})"
        logger.info(msg)
        if self.debug:
            print(f"[API MON] {msg}")
```
---
## def snapshot:
#### Возвращает текущую сводку по статистике API.

Сводка включает:
- total: Общее количество запросов
- by_path: Счетчик запросов по пути
- by_method: Счетчик по HTTP-методам
- by_status: Счетчик по статусам ответа
- avg_latency_ms: Среднее время обработки по каждому пути (ms)

#### Возвращает
| Тип | Описание |
|-----|----------|
| `dict` | Статистика API в виде словаря |

```python
    def snapshot(self) -> dict:
        """Возвращает текущую сводку по статистике API.

        Сводка включает:
            - total: Общее количество запросов
            - by_path: Счетчик запросов по пути
            - by_method: Счетчик по HTTP-методам
            - by_status: Счетчик по статусам ответа
            - avg_latency_ms: Среднее время обработки по каждому пути (ms)

        Returns:
            dict: Статистика API в виде словаря
        """
        with self._lock:
            avg_latency = {
                p: (sum(lst) / len(lst)) if lst else 0.0 for p, lst in self.latencies.items()
            }
            return {
                "total": self.total_requests,
                "by_path": dict(self.by_path),
                "by_method": dict(self.by_method),
                "by_status": dict(self.by_status),
                "avg_latency_ms": avg_latency,
            }
```
---