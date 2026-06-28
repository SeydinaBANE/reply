from prometheus_client import Counter, Histogram

REQUEST_LATENCY = Histogram(
    "model_request_latency_seconds",
    "Latency of model inference requests",
    labelnames=("model",),
)

REQUEST_ERRORS = Counter(
    "model_request_errors_total",
    "Total number of failed inference requests",
    labelnames=("model",),
)

TOKENS_USED = Counter(
    "model_tokens_total",
    "Total tokens consumed by LLM calls",
    labelnames=("model",),
)


def observe_request(model: str, latency_seconds: float, failed: bool) -> None:
    REQUEST_LATENCY.labels(model=model).observe(latency_seconds)
    if failed:
        REQUEST_ERRORS.labels(model=model).inc()


def add_tokens(model: str, tokens: int) -> None:
    TOKENS_USED.labels(model=model).inc(tokens)
