# Модуль api_monitor

Функция для мониторинга скорости API.

## Класс ApiMonitor

**Простой монитор API запросов с логированием в файл.**

---
## def init:
#### Конструктор.

```python
    def __init__(self) -> None:
        """Конструктор."""
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
#### Счётчик.

```python
    def record(self, path: str, method: str, status: int, latency_ms: float) -> None:
        """Счётчик."""
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
#### Возвращает функцию с avg_latency.

```python
    def snapshot(self) -> dict:
        """Возвращает функцию с avg_latency."""
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