import time
from collections.abc import Awaitable, Callable

from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.requests import Request
from starlette.responses import Response

from inference.metrics import HTTP_LATENCY


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


def render_metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
