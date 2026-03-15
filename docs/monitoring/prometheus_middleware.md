## Класс PrometheusMiddleware


```python
class PrometheusMiddleware(ASGIMiddleware):
```

---
## async def handle:

```python
    async def handle(self, scope: Scope, receive: Receive, send: Send, next_app):
        if scope.get("type") != "http":
            await next_app(scope, receive, send)
            return

        IN_FLIGHT.inc()
        start = time.time()

        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "UNKNOWN")

        async def send_wrapper(message):
            if message.get("type") == "http.response.start":
                status = str(message.get("status", 200))
                HTTP_REQUESTS.labels(method=method, path=path, status=status).inc()

                # Отслеживаем все ошибки >=400
                if int(status) >= 400:
                    HTTP_ERRORS.labels(method=method, path=path, status=status).inc()
            await send(message)

        try:
            await next_app(scope, receive, send_wrapper)
        except TooManyRequestsError as exc:
            status = "429"
            HTTP_ERRORS.labels(method=method, path=path, status=status).inc()
            raise
        except Exception:
            status = "500"
            HTTP_ERRORS.labels(method=method, path=path, status=status).inc()
            raise
        finally:
            elapsed = time.time() - start
            HTTP_LATENCY.labels(method=method, path=path).observe(elapsed)
            IN_FLIGHT.dec()
```
---