import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from redis.asyncio import Redis
from redis.exceptions import RedisError

from inference.audit import LoggingAuditLogger
from inference.auth import ApiKeyProvider
from inference.backend import build_backend
from inference.config import Settings, load_settings
from inference.errors import (
    BackendError,
    InferenceError,
    RateLimiterUnavailableError,
    RateLimitExceededError,
    UnauthorizedError,
)
from inference.instrumentation import prometheus_middleware, render_metrics
from inference.metrics import (
    AUTH_FAILURES,
    BACKEND_ERRORS,
    RATE_LIMITED,
    RATELIMIT_REDIS_FAILURES,
    TOKENS_TOTAL,
)
from inference.models import CompletionRequest, CompletionResponse
from inference.ratelimit import RateLimiter
from inference.service import InferenceService
from inference.vault_client import (
    HvacSecretReader,
    KubernetesAuthReader,
    SecretReader,
    VaultClient,
)

logger = logging.getLogger(__name__)


@dataclass
class AppState:
    redis: Redis
    vault: VaultClient
    service: InferenceService
    http_client: httpx.AsyncClient | None


def build_vault(settings: Settings) -> VaultClient:
    reader: SecretReader
    if settings.vault_auth == "kubernetes":
        reader = KubernetesAuthReader(settings.vault_addr, settings.vault_role)
    else:
        reader = HvacSecretReader(settings.vault_addr, settings.vault_token)
    return VaultClient(reader)


async def build_state(settings: Settings) -> AppState:
    redis: Redis = Redis.from_url(
        settings.redis_url,
        socket_timeout=settings.redis_socket_timeout,
        socket_connect_timeout=settings.redis_socket_timeout,
        health_check_interval=30,
    )
    vault = build_vault(settings)

    def load_api_keys() -> list[str]:
        return vault.read_secret(settings.vault_secret_path, "api_keys").split(",")

    http_client: httpx.AsyncClient | None = None
    backend_api_key = ""
    if settings.backend == "vllm":
        http_client = httpx.AsyncClient(
            base_url=settings.backend_url, timeout=settings.backend_timeout_s
        )
        backend_api_key = vault.read_secret(settings.vault_secret_path, "backend_api_key")
    service = InferenceService(
        ApiKeyProvider(load_api_keys, settings.api_key_refresh_s),
        RateLimiter(
            redis,
            settings.rate_limit_per_minute,
            fail_open=settings.rate_limit_fail_open,
            on_failure=lambda: RATELIMIT_REDIS_FAILURES.inc(),
        ),
        build_backend(settings, http_client, backend_api_key),
        LoggingAuditLogger(),
    )
    return AppState(redis=redis, vault=vault, service=service, http_client=http_client)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    state = await build_state(load_settings())
    app.state.inference = state
    try:
        yield
    finally:
        if state.http_client is not None:
            await state.http_client.aclose()
        await state.redis.aclose()


app = FastAPI(title="llm-secure-inference", lifespan=lifespan)
app.middleware("http")(prometheus_middleware)


@app.get("/metrics")
async def metrics() -> Response:
    return render_metrics()


def get_state(request: Request) -> AppState:
    state: AppState = request.app.state.inference
    return state


def parse_bearer(authorization: str | None) -> str:
    if authorization is None:
        raise UnauthorizedError("missing authorization header")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise UnauthorizedError("malformed authorization header")
    return token


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
async def readyz(state: AppState = Depends(get_state)) -> dict[str, str]:
    try:
        await state.redis.ping()
        await asyncio.to_thread(state.vault.health)
    except RedisError as exc:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail="redis unavailable"
        ) from exc
    except InferenceError as exc:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail="vault unavailable"
        ) from exc
    return {"status": "ready"}


@app.post("/v1/completions", response_model=CompletionResponse)
async def completions(
    request: CompletionRequest,
    response: Response,
    authorization: str | None = Header(default=None),
    state: AppState = Depends(get_state),
) -> CompletionResponse:
    try:
        api_key = parse_bearer(authorization)
        completion, remaining = await state.service.complete(
            api_key, request.prompt, request.max_tokens
        )
    except UnauthorizedError as exc:
        AUTH_FAILURES.inc()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except RateLimitExceededError as exc:
        RATE_LIMITED.inc()
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc
    except RateLimiterUnavailableError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except BackendError as exc:
        BACKEND_ERRORS.inc()
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    TOKENS_TOTAL.inc(completion.tokens)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    return CompletionResponse(
        completion=completion.text, tokens=completion.tokens, remaining=remaining
    )
