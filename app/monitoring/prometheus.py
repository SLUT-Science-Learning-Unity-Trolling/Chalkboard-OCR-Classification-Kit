# app/monitoring/prometheus.py
from functools import wraps
import json
import time
from prometheus_client import REGISTRY, generate_latest, CONTENT_TYPE_LATEST

from app.monitoring.prometheus_mongo import MONGO_OPS, MONGO_LATENCY, MONGO_ERRORS, MONGO_ACTIVE_CONN, monitored_mongo_call
from app.monitoring.prometheus_redis import REDIS_OPS, REDIS_LATENCY, REDIS_ERRORS, monitor_redis
from prometheus_client import Counter, Histogram, Gauge

HTTP_REQUESTS = Counter(
    "app_http_requests_total", "Total HTTP requests", ["method", "path", "status"]
)
HTTP_LATENCY = Histogram(
    "app_http_request_latency_seconds", "HTTP request latency seconds", ["method", "path"]
)
IN_FLIGHT = Gauge("app_in_flight_requests", "In-flight HTTP requests")

HTTP_ERRORS = Counter(
    "app_http_errors",
    "HTTP requests resulting in errors",
    ["method", "path", "status"]
)

OCR_PROCESSED = Counter("app_ocr_processed_total", "OCR images processed")
OCR_ERRORS = Counter("app_ocr_errors_total", "OCR processing errors")
OCR_LATENCY = Histogram("app_ocr_latency_seconds", "OCR processing latency seconds")

def metrics_endpoint() -> tuple[bytes, str]:
    """Возвращает все метрики в формате Prometheus"""
    return generate_latest(), CONTENT_TYPE_LATEST

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
