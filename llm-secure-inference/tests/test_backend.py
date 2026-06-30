from collections.abc import Callable

import httpx
import pytest

from inference.backend import EchoBackend, VllmBackend
from inference.errors import BackendError


@pytest.mark.asyncio
async def test_echo_backend_truncates_to_max_tokens() -> None:
    completion = await EchoBackend().complete("one two three four", max_tokens=2)
    assert completion.text == "one two"
    assert completion.tokens == 2


def _backend(handler: Callable[[httpx.Request], httpx.Response]) -> VllmBackend:
    client = httpx.AsyncClient(base_url="http://vllm", transport=httpx.MockTransport(handler))
    return VllmBackend(client, model="m", api_key="key", timeout_s=5.0)


@pytest.mark.asyncio
async def test_vllm_backend_returns_completion() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={"choices": [{"text": "hi there"}], "usage": {"completion_tokens": 2}}
        )

    completion = await _backend(handler).complete("prompt", 16)
    assert completion.text == "hi there"
    assert completion.tokens == 2


@pytest.mark.asyncio
async def test_vllm_backend_raises_on_http_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "boom"})

    with pytest.raises(BackendError):
        await _backend(handler).complete("prompt", 16)


@pytest.mark.asyncio
async def test_vllm_backend_raises_on_malformed_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": True})

    with pytest.raises(BackendError):
        await _backend(handler).complete("prompt", 16)


@pytest.mark.asyncio
async def test_vllm_backend_raises_on_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    with pytest.raises(BackendError):
        await _backend(handler).complete("prompt", 16)
