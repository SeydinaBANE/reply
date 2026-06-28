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
