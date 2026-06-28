import time
from collections.abc import Awaitable, Callable

from prometheus_client import Histogram
from starlette.requests import Request
from starlette.responses import Response

HTTP_LATENCY = Histogram(
    "http_request_latency_seconds",
    "Latency of API requests",
    labelnames=("method", "path"),
)


async def prometheus_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    start = time.perf_counter()
    response = await call_next(request)
    HTTP_LATENCY.labels(method=request.method, path=request.url.path).observe(
        time.perf_counter() - start
    )
    return response
