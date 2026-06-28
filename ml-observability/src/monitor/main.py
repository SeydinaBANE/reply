import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

import asyncpg
from fastapi import Depends, FastAPI, Request, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from redis.asyncio import Redis

from monitor.alerts import AlertPublisher
from monitor.config import Settings, load_settings
from monitor.instrumentation import prometheus_middleware
from monitor.metrics import observe_request
from monitor.monitoring import evaluate_drift
from monitor.schemas import DriftRequest, DriftResponse, LogRequest
from monitor.store import PredictionStore

logger = logging.getLogger(__name__)


@dataclass
class AppState:
    pool: asyncpg.Pool
    redis: Redis
    store: PredictionStore
    alerts: AlertPublisher
    settings: Settings


async def build_state(settings: Settings) -> AppState:
    pool = await asyncpg.create_pool(settings.database_url)
    redis: Redis = Redis.from_url(settings.redis_url)
    return AppState(
        pool=pool,
        redis=redis,
        store=PredictionStore(pool),
        alerts=AlertPublisher(redis),
        settings=settings,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    state = await build_state(load_settings())
    app.state.monitor = state
    try:
        yield
    finally:
        await state.pool.close()
        await state.redis.aclose()


app = FastAPI(title="ml-observability", lifespan=lifespan)
app.middleware("http")(prometheus_middleware)


def get_state(request: Request) -> AppState:
    state: AppState = request.app.state.monitor
    return state


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
async def readyz(state: AppState = Depends(get_state)) -> dict[str, str]:
    await state.pool.fetchval("SELECT 1")
    return {"status": "ready"}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/log", status_code=status.HTTP_201_CREATED)
async def log_prediction(
    request: LogRequest,
    state: AppState = Depends(get_state),
) -> dict[str, str]:
    observe_request(request.model, request.latency_ms / 1000.0, failed=False)
    await state.store.record(
        request.model, request.features, request.prediction, request.latency_ms
    )
    return {"status": "recorded"}


@app.post("/drift", response_model=DriftResponse)
async def check_drift(
    request: DriftRequest,
    state: AppState = Depends(get_state),
) -> DriftResponse:
    result = evaluate_drift(
        request.reference,
        request.current,
        state.settings.psi_warning_threshold,
        state.settings.psi_critical_threshold,
    )
    await state.alerts.publish(request.model, result)
    return DriftResponse(psi=result.psi, level=result.level.value)
