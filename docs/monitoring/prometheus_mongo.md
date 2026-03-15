## async def monitored_mongo_call:
#### Wrapper to monitor MongoDB calls.

```python
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
```
---