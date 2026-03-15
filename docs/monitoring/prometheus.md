## def metrics_endpoint:
#### Возвращает все метрики в формате Prometheus

```python
def metrics_endpoint() -> tuple[bytes, str]:
    """Возвращает все метрики в формате Prometheus"""
    return generate_latest(), CONTENT_TYPE_LATEST
```
---
## def metrics_as_json:
#### Возвращает все метрики в виде читаемого JSON.

Используется для дебага и удобного вывода.

```python
def metrics_as_json() -> str:
    """
    Возвращает все метрики в виде читаемого JSON.
    Используется для дебага и удобного вывода.
    """
    data = {}
    for metric in REGISTRY.collect():
        if metric.name.endswith("_created"):
            continue

        seen = set()
        samples = []
        for s in metric.samples:
            key = (frozenset(s.labels.items()), s.value)
            if key not in seen:
                seen.add(key)
                samples.append({"labels": s.labels, "value": s.value})

        data[metric.name] = {"type": metric.type, "samples": samples}

    return json.dumps(data, indent=2, ensure_ascii=False)
```
---