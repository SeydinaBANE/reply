from fastapi import Depends, FastAPI, HTTPException, status

from inference.errors import RateLimitExceededError
from inference.ratelimit import RateLimiter

app = FastAPI(title="llm-secure-inference")


def get_rate_limiter() -> RateLimiter:
    raise NotImplementedError("wire RateLimiter via lifespan / dependency override")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/completions")
async def completions(
    prompt: str,
    api_key: str,
    limiter: RateLimiter = Depends(get_rate_limiter),
) -> dict[str, object]:
    try:
        remaining = await limiter.check(api_key)
    except RateLimitExceededError as exc:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc
    return {"completion": "", "remaining": remaining}
