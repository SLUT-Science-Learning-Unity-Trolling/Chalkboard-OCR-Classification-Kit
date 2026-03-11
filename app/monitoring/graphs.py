import json
import requests
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
from collections import defaultdict
from typing import List, Dict, Any, Optional


def is_probable_timestamp(v: float) -> bool:
    """Возвращает True для значений, похожих на epoch seconds (>= 1e9)."""
    try:
        return float(v) >= 1e9
    except Exception:
        return False

def safe_float_or_none(v: Any) -> Optional[float]:
    """Пытаемся привести к float. Если value похож на timestamp -> возвращаем None."""
    try:
        fv = float(v)
    except Exception:
        return None
    if is_probable_timestamp(fv):
        return None
    return fv

def extract_samples(metrics: dict, metric_name: str, label_keys: List[str]) -> List[Dict[str, Any]]:
    """
    Универсально извлекает samples для счетчиков/гейджей.
    Возвращает список dict'ов с ключами из label_keys и 'value'.
    Пропускает значения, которые похожи на timestamp.
    """
    out: List[Dict[str, Any]] = []
    for s in metrics.get(metric_name, {}).get("samples", []):
        labels = s.get("labels", {}) or {}
        raw_val = s.get("value", None)
        val = safe_float_or_none(raw_val)
        if val is None:
            continue
        row = {k: labels.get(k, "unknown") for k in label_keys}
        row["value"] = val
        out.append(row)
    return out

def extract_gauge_value(metrics: dict, metric_name: str) -> float:
    """
    Берёт первый валидный (не-timestamp) sample.value для gauge-метрики.
    Если ничего не найдено — возвращает 0.
    """
    for s in metrics.get(metric_name, {}).get("samples", []):
        val = safe_float_or_none(s.get("value", None))
        if val is not None:
            return val
    return 0.0

def extract_histogram(metrics: dict, metric_name: str, label_keys: List[str]) -> List[Dict[str, Any]]:
    """
    Извлекает bucket-гистограммы: возвращает список с "latency"/"count" и прочими label'ами.
    Для le: заменяем '+Inf' на 100.0 (arbitrary large bucket) и приводим к float.
    Пропускаем timestamp-like values.
    """
    out: List[Dict[str, Any]] = []
    for s in metrics.get(metric_name, {}).get("samples", []):
        labels = s.get("labels", {}) or {}
        if "le" not in labels:
            continue
        le_raw = labels.get("le")
        try:
            le_val = float(le_raw.replace("+Inf", "100"))
        except Exception:
            continue
        val = safe_float_or_none(s.get("value", None))
        if val is None:
            continue
        row = {k: labels.get(k, "unknown") for k in label_keys}
        row["latency"] = le_val
        row["count"] = val
        out.append(row)
    return out


def fetch_metrics() -> dict:
    """Получаем метрики из локального Prometheus JSON эндпоинта"""
    r = requests.get("http://localhost:8000/health/metrics/json")
    return r.json()


def create_gc_fig(metrics: dict):
    fig = go.Figure()

    df_gc = pd.DataFrame(extract_samples(metrics, "python_gc_collections", ["generation"]))
    if not df_gc.empty:
        fig.add_trace(go.Bar(x=df_gc["generation"], y=df_gc["value"], name="GC Collections"))

    df_collected = pd.DataFrame(extract_samples(metrics, "python_gc_objects_collected", ["generation"]))
    if not df_collected.empty:
        fig.add_trace(go.Bar(x=df_collected["generation"], y=df_collected["value"], name="Objects Collected"))

    df_uncollectable = pd.DataFrame(extract_samples(metrics, "python_gc_objects_uncollectable", ["generation"]))
    if not df_uncollectable.empty:
        fig.add_trace(go.Bar(x=df_uncollectable["generation"], y=df_uncollectable["value"], name="Uncollectable"))

    fig.update_layout(title="GC Metrics", barmode="group", height=400, xaxis={"automargin": True})
    return fig

def create_process_fig(metrics: dict):
    fig = go.Figure()

    vm = extract_gauge_value(metrics, "process_virtual_memory_bytes")
    resident = extract_gauge_value(metrics, "process_resident_memory_bytes")
    df_mem = pd.DataFrame([
        {"metric": "virtual_memory", "value": vm},
        {"metric": "resident_memory", "value": resident},
    ])
    fig.add_trace(go.Bar(x=df_mem["metric"], y=df_mem["value"], name="Memory Bytes"))

    cpu = extract_gauge_value(metrics, "process_cpu_seconds")
    df_cpu = pd.DataFrame([{"metric": "cpu_seconds", "value": cpu}])
    fig.add_trace(go.Bar(x=df_cpu["metric"], y=df_cpu["value"], name="CPU Seconds"))

    open_fds = extract_gauge_value(metrics, "process_open_fds")
    max_fds = extract_gauge_value(metrics, "process_max_fds")
    df_fds = pd.DataFrame([
        {"metric": "open_fds", "value": open_fds},
        {"metric": "max_fds", "value": max_fds},
    ])
    fig.add_trace(go.Bar(x=df_fds["metric"], y=df_fds["value"], name="File Descriptors"))

    fig.update_layout(title="Process Metrics", barmode="group", height=400, xaxis={"automargin": True})
    return fig

def create_redis_fig(metrics: dict):
    fig = go.Figure()

    ops = extract_samples(metrics, "app_redis_ops", ["operation"])
    if ops:
        df_ops = pd.DataFrame(ops).groupby("operation", as_index=False).sum()
        fig.add_trace(go.Bar(x=df_ops["operation"], y=df_ops["value"], name="Redis Ops"))

    hist_rows = extract_histogram(metrics, "app_redis_latency_seconds", ["operation"])
    if hist_rows:
        df_hist = pd.DataFrame(hist_rows)
        for op in df_hist["operation"].unique():
            df_op = df_hist[df_hist["operation"] == op].sort_values("latency")
            fig.add_trace(go.Bar(x=df_op["latency"], y=df_op["count"], name=f"Latency {op}"))

    fig.update_layout(title="Redis Metrics", barmode="group", height=400, xaxis={"automargin": True})
    return fig

def create_mongo_fig(metrics: dict):
    fig = go.Figure()

    ops = extract_samples(metrics, "app_mongo_ops", ["operation"])
    if ops:
        df_ops = pd.DataFrame(ops).groupby("operation", as_index=False).sum()
        fig.add_trace(go.Bar(x=df_ops["operation"], y=df_ops["value"], name="Mongo Ops"))

    errs = extract_samples(metrics, "app_mongo_errors", ["operation"])
    if errs:
        df_errs = pd.DataFrame(errs).groupby("operation", as_index=False).sum()
        fig.add_trace(go.Bar(x=df_errs["operation"], y=df_errs["value"], name="Mongo Errors"))

    hist_rows = extract_histogram(metrics, "app_mongo_latency_seconds", ["operation"])
    if hist_rows:
        df_hist = pd.DataFrame(hist_rows)
        for op in df_hist["operation"].unique():
            df_op = df_hist[df_hist["operation"] == op].sort_values("latency")
            fig.add_trace(go.Bar(x=df_op["latency"], y=df_op["count"], name=f"Latency {op}"))

    active_conn = extract_gauge_value(metrics, "app_mongo_active_connections")
    fig.add_trace(go.Bar(x=["active_connections"], y=[active_conn], name="Active Connections"))

    fig.update_layout(title="Mongo Metrics", barmode="group", height=600, xaxis={"automargin": True})
    return fig

def create_http_fig(metrics: dict):
    """
    Для каждого endpoint (method + path) агрегируем:
      - Success: сумма значений для status < 400 (из app_http_requests)
      - Error: сумма значений для status >= 400 (из app_http_requests) + app_http_errors
      - In-Flight: текущее значение gauges app_in_flight_requests (одинаковое для всех)
    """
    agg = defaultdict(lambda: {"success": 0.0, "error": 0.0})

    req_rows = extract_samples(metrics, "app_http_requests", ["method", "path", "status"])
    for r in req_rows:
        try:
            status = int(r.get("status", -1))
        except Exception:
            continue
        key = f"{r.get('method','unknown')} {r.get('path','unknown')}"
        if status < 400:
            agg[key]["success"] += r["value"]
        else:
            agg[key]["error"] += r["value"]

    err_rows = extract_samples(metrics, "app_http_errors", ["method", "path", "status"])
    for r in err_rows:
        key = f"{r.get('method','unknown')} {r.get('path','unknown')}"
        agg[key]["error"] += r["value"]

    inflight_val = extract_gauge_value(metrics, "app_in_flight_requests")
    for key in agg:
        agg[key]["in_flight"] = inflight_val

    df = pd.DataFrame([
        {"endpoint": k, "Success": v["success"], "Error": v["error"], "In-Flight": v.get("in_flight", 0)}
        for k, v in agg.items()
    ])

    fig = go.Figure()
    if df.empty:
        fig.add_annotation(text="No HTTP data", showarrow=False)
        fig.update_layout(title="HTTP Metrics (aggregated per endpoint)", height=250)
        return fig

    df["total"] = df["Success"] + df["Error"] + df["In-Flight"]
    df = df.sort_values("total", ascending=False).reset_index(drop=True)

    for col, color in zip(["Success", "Error", "In-Flight"], ["green", "red", "orange"]):
        fig.add_trace(go.Bar(
            x=df["endpoint"],
            y=df[col],
            name=col,
            marker_color=color
        ))

    fig.update_layout(
        title="HTTP Metrics (aggregated per endpoint)",
        barmode="group",
        height=450,
        xaxis={"automargin": True}
    )
    return fig

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Server Metrics Dashboard"),
    dcc.Tabs(id="tabs", value="gc", children=[
        dcc.Tab(label="GC", value="gc"),
        dcc.Tab(label="Process", value="process"),
        dcc.Tab(label="Redis", value="redis"),
        dcc.Tab(label="Mongo", value="mongo"),
        dcc.Tab(label="HTTP", value="http"),
    ]),
    html.Div(id="tabs-content"),
    dcc.Interval(id="interval-component", interval=5 * 1000, n_intervals=0)
])

@app.callback(
    Output("tabs-content", "children"),
    Input("tabs", "value"),
    Input("interval-component", "n_intervals")
)
def render_tab(tab, n):
    metrics = fetch_metrics()
    if tab == "gc":
        return dcc.Graph(figure=create_gc_fig(metrics))
    elif tab == "process":
        return dcc.Graph(figure=create_process_fig(metrics))
    elif tab == "redis":
        return dcc.Graph(figure=create_redis_fig(metrics))
    elif tab == "mongo":
        return dcc.Graph(figure=create_mongo_fig(metrics))
    elif tab == "http":
        return dcc.Graph(figure=create_http_fig(metrics))
    return html.Div("Нет данных")

# -------------------------
if __name__ == "__main__":
    app.run(debug=True)