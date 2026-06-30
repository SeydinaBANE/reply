import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from redis.asyncio import Redis

from inference.audit import LoggingAuditLogger
from inference.auth import ApiKeyAuthenticator
from inference.backend import EchoBackend
from inference.config import Settings, load_settings
from inference.errors import (
    BackendError,
    RateLimiterUnavailableError,
    RateLimitExceededError,
    UnauthorizedError,
)
from inference.models import CompletionRequest, CompletionResponse
from inference.ratelimit import RateLimiter
from inference.service import InferenceService
from inference.vault_client import HvacSecretReader, VaultClient

logger = logging.getLogger(__name__)


@dataclass
class AppState:
    redis: Redis
    service: InferenceService


async def build_state(settings: Settings) -> AppState:
    redis: Redis = Redis.from_url(settings.redis_url)
    vault = VaultClient(HvacSecretReader(settings.vault_addr, settings.vault_token))
    api_keys = vault.read_secret(settings.vault_secret_path, "api_keys").split(",")
    service = InferenceService(
        ApiKeyAuthenticator(api_keys),
        RateLimiter(
            redis,
            settings.rate_limit_per_minute,
            fail_open=settings.rate_limit_fail_open,
        ),
        EchoBackend(),
        LoggingAuditLogger(),
    )
    return AppState(redis=redis, service=service)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    state = await build_state(load_settings())
    app.state.inference = state
    try:
        yield
    finally:
        await state.redis.aclose()


app = FastAPI(title="llm-secure-inference", lifespan=lifespan)


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
    await state.redis.ping()
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
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except RateLimitExceededError as exc:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc
    except RateLimiterUnavailableError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except BackendError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    response.headers["X-RateLimit-Remaining"] = str(remaining)
    return CompletionResponse(
        completion=completion.text, tokens=completion.tokens, remaining=remaining
    )
