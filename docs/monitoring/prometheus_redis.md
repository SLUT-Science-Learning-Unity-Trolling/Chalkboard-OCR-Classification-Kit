# Модуль prometheus_redis

Prometheus метрики для Redis репозиториев.

## async def monitor_redis:
#### Обертка для мониторинга Redis операций.

```python
async def monitor_redis(operation: str, coro):
    """Обертка для мониторинга Redis операций."""
    start = time.time()
    try:
        result = await coro
        return result
    except Exception:
        REDIS_ERRORS.labels(operation=operation).inc()
        raise
    finally:
        duration = time.time() - start
        REDIS_LATENCY.labels(operation=operation).observe(duration)
        REDIS_OPS.labels(operation=operation).inc()
```
---