from prometheus_client import Counter, Gauge, Histogram

MONGO_OPS = Counter(
    "app_mongo_ops_total", "Total MongoDB operations", ["operation"]
)
MONGO_LATENCY = Histogram(
    "app_mongo_latency_seconds",
    "MongoDB operation latency seconds",
    ["operation"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)
MONGO_ERRORS = Counter(
    "app_mongo_errors_total", "MongoDB errors", ["operation"]
)
MONGO_ACTIVE_CONN = Gauge("app_mongo_active_connections", "Active MongoDB connections")

async def monitored_mongo_call(operation: str, coro):
    """Wrapper to monitor MongoDB calls."""
    import time
    start = time.time()
    try:
        result = await coro
        return result
    except Exception as e:
        MONGO_ERRORS.labels(operation=operation).inc()
        raise
    finally:
        duration = time.time() - start
        MONGO_LATENCY.labels(operation=operation).observe(duration)
        MONGO_OPS.labels(operation=operation).inc()
