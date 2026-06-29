from prometheus_client import Counter, Histogram

REQUESTS = Counter(
    "rag_requests_total",
    "Total HTTP requests handled",
    labelnames=("method", "path", "status"),
)

REQUEST_LATENCY = Histogram(
    "rag_request_duration_seconds",
    "HTTP request latency in seconds",
    labelnames=("method", "path"),
)

CACHE_EVENTS = Counter(
    "rag_embedding_cache_events_total",
    "Embedding cache hits and misses",
    labelnames=("result",),
)

VERTEX_ERRORS = Counter(
    "rag_vertex_errors_total",
    "Vertex AI call failures",
    labelnames=("operation",),
)
