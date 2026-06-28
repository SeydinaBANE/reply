import logging
from typing import Protocol

from rag_service.embeddings import CachedEmbedder
from rag_service.errors import EmptyCorpusError
from rag_service.models import Passage

logger = logging.getLogger(__name__)


class VectorStore(Protocol):
    async def search(self, embedding: list[float], top_k: int) -> list[Passage]: ...

    async def count(self) -> int: ...


class Retriever:
    def __init__(self, embedder: CachedEmbedder, store: VectorStore, top_k: int) -> None:
        self._embedder = embedder
        self._store = store
        self._top_k = top_k

    async def retrieve(self, question: str, top_k: int | None = None) -> list[Passage]:
        if await self._store.count() == 0:
            raise EmptyCorpusError("no documents indexed")
        embedding = await self._embedder.embed(question)
        limit = top_k if top_k is not None else self._top_k
        passages = await self._store.search(embedding, limit)
        logger.info("retrieved %d passages for question", len(passages))
        return passages
