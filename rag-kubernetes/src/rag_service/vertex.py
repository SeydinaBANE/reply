import asyncio
import logging
from collections.abc import Callable
from typing import Protocol, TypeVar, cast

from rag_service.errors import EmbeddingError, GenerationError, RagError
from rag_service.metrics import VERTEX_ERRORS

logger = logging.getLogger(__name__)

T = TypeVar("T")


class EmbeddingClient(Protocol):
    def get_embeddings(self, texts: list[str]) -> list["_HasValues"]: ...


class _HasValues(Protocol):
    @property
    def values(self) -> list[float]: ...


class GenerationClient(Protocol):
    def generate_content(self, prompt: str) -> "_HasText": ...


class _HasText(Protocol):
    @property
    def text(self) -> str: ...


async def _call_with_retry(
    func: Callable[[], T],
    operation: str,
    timeout: float,
    max_attempts: int,
    backoff_base: float,
    error_cls: type[RagError],
) -> T:
    loop = asyncio.get_running_loop()
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return await asyncio.wait_for(loop.run_in_executor(None, func), timeout)
        except Exception as exc:
            last_exc = exc
            logger.warning("vertex call failed (attempt %d/%d): %s", attempt, max_attempts, exc)
            if attempt < max_attempts:
                await asyncio.sleep(backoff_base * (2 ** (attempt - 1)))
    VERTEX_ERRORS.labels(operation=operation).inc()
    raise error_cls(str(last_exc)) from last_exc


class VertexEmbeddingBackend:
    def __init__(
        self,
        project: str,
        location: str,
        model: str,
        timeout: float,
        max_attempts: int,
        backoff_base: float,
        client: EmbeddingClient | None = None,
    ) -> None:
        self._timeout = timeout
        self._max_attempts = max_attempts
        self._backoff_base = backoff_base
        self._client = client if client is not None else self._load_client(project, location, model)

    @staticmethod
    def _load_client(project: str, location: str, model: str) -> EmbeddingClient:
        import vertexai
        from vertexai.language_models import TextEmbeddingModel

        vertexai.init(project=project, location=location)
        return cast(EmbeddingClient, TextEmbeddingModel.from_pretrained(model))

    async def embed(self, text: str) -> list[float]:
        embeddings = await _call_with_retry(
            lambda: self._client.get_embeddings([text]),
            "embed",
            self._timeout,
            self._max_attempts,
            self._backoff_base,
            EmbeddingError,
        )
        return list(embeddings[0].values)


class VertexGenerator:
    def __init__(
        self,
        project: str,
        location: str,
        model: str,
        timeout: float,
        max_attempts: int,
        backoff_base: float,
        client: GenerationClient | None = None,
    ) -> None:
        self._timeout = timeout
        self._max_attempts = max_attempts
        self._backoff_base = backoff_base
        self._client = client if client is not None else self._load_client(project, location, model)

    @staticmethod
    def _load_client(project: str, location: str, model: str) -> GenerationClient:
        import vertexai
        from vertexai.generative_models import GenerativeModel

        vertexai.init(project=project, location=location)
        return cast(GenerationClient, GenerativeModel(model))

    async def generate(self, prompt: str) -> str:
        response = await _call_with_retry(
            lambda: self._client.generate_content(prompt),
            "generate",
            self._timeout,
            self._max_attempts,
            self._backoff_base,
            GenerationError,
        )
        return str(response.text)
