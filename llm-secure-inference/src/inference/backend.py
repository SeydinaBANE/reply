import asyncio
from dataclasses import dataclass
from typing import Protocol

import httpx

from inference.config import Settings
from inference.errors import BackendError


@dataclass(frozen=True)
class Completion:
    text: str
    tokens: int


class LlmBackend(Protocol):
    async def complete(self, prompt: str, max_tokens: int) -> Completion: ...


class EchoBackend:
    async def complete(self, prompt: str, max_tokens: int) -> Completion:
        words = prompt.split()[:max_tokens]
        return Completion(text=" ".join(words), tokens=len(words))


class VllmBackend:
    def __init__(
        self, client: httpx.AsyncClient, model: str, api_key: str, timeout_s: float
    ) -> None:
        self._client = client
        self._model = model
        self._api_key = api_key
        self._timeout_s = timeout_s

    async def complete(self, prompt: str, max_tokens: int) -> Completion:
        payload = {"model": self._model, "prompt": prompt, "max_tokens": max_tokens}
        headers = {"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}
        try:
            async with asyncio.timeout(self._timeout_s):
                response = await self._client.post(
                    "/v1/completions", json=payload, headers=headers
                )
            response.raise_for_status()
            body = response.json()
        except (httpx.HTTPError, TimeoutError) as exc:
            raise BackendError(str(exc)) from exc
        return _parse_completion(body)


class VertexBackend:
    def __init__(self, project: str, location: str, model: str, timeout_s: float) -> None:
        self._project = project
        self._location = location
        self._model = model
        self._timeout_s = timeout_s

    async def complete(self, prompt: str, max_tokens: int) -> Completion:
        try:
            async with asyncio.timeout(self._timeout_s):
                return await asyncio.to_thread(self._predict, prompt, max_tokens)
        except TimeoutError as exc:
            raise BackendError(f"vertex backend timed out: {exc}") from exc
        except Exception as exc:
            raise BackendError(f"vertex backend failed: {exc}") from exc

    def _predict(self, prompt: str, max_tokens: int) -> Completion:
        import vertexai
        from vertexai.generative_models import GenerationConfig, GenerativeModel

        vertexai.init(project=self._project, location=self._location)
        model = GenerativeModel(self._model)
        result = model.generate_content(
            prompt, generation_config=GenerationConfig(max_output_tokens=max_tokens)
        )
        text = str(result.text)
        return Completion(text=text, tokens=len(text.split()))


def _parse_completion(body: object) -> Completion:
    if not isinstance(body, dict):
        raise BackendError("backend response is not an object")
    choices = body.get("choices")
    if not isinstance(choices, list) or not choices:
        raise BackendError("backend response missing choices")
    first = choices[0]
    if not isinstance(first, dict) or "text" not in first:
        raise BackendError("backend choice missing text")
    text = str(first["text"])
    usage = body.get("usage")
    if isinstance(usage, dict) and isinstance(usage.get("completion_tokens"), int):
        return Completion(text=text, tokens=int(usage["completion_tokens"]))
    return Completion(text=text, tokens=len(text.split()))


def build_backend(
    settings: Settings, client: httpx.AsyncClient | None, api_key: str
) -> LlmBackend:
    if settings.backend == "echo":
        return EchoBackend()
    if settings.backend == "vllm":
        if client is None:
            raise BackendError("vllm backend requires an http client")
        return VllmBackend(client, settings.backend_model, api_key, settings.backend_timeout_s)
    return VertexBackend(
        settings.vertex_project,
        settings.vertex_location,
        settings.backend_model,
        settings.backend_timeout_s,
    )
