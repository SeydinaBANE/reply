from prometheus_client import Counter, Histogram

HTTP_LATENCY = Histogram(
    "http_request_latency_seconds",
    "Latency of API requests",
    labelnames=("method", "path"),
)

TOKENS_TOTAL = Counter(
    "inference_tokens_total",
    "Total number of tokens returned to clients",
)

AUTH_FAILURES = Counter(
    "inference_auth_failures_total",
    "Total number of rejected API keys",
)

RATE_LIMITED = Counter(
    "inference_rate_limited_total",
    "Total number of requests blocked by the rate limiter",
)

BACKEND_ERRORS = Counter(
    "inference_backend_errors_total",
    "Total number of LLM backend failures",
)

RATELIMIT_REDIS_FAILURES = Counter(
    "ratelimit_redis_failures_total",
    "Total number of rate-limiter Redis failures (fail-open events)",
)
