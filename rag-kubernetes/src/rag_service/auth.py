import hmac

from fastapi import HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader

_API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(
    request: Request,
    provided: str | None = Security(_API_KEY_HEADER),
) -> None:
    expected: str = request.app.state.rag.api_key
    if provided is None or not hmac.compare_digest(provided, expected):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
