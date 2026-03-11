"""Prometheus метрики для Redis репозиториев."""
# prometheus_redis.py

import time
from prometheus_client import Counter, Histogram

REDIS_OPS = Counter(
    "app_redis_ops_total", "Total Redis operations", ["operation"]
)
REDIS_LATENCY = Histogram(
    "app_redis_latency_seconds",
    "Redis operation latency seconds",
    ["operation"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)
REDIS_ERRORS = Counter(
    "app_redis_errors_total", "Redis operation errors", ["operation"]
)

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