import logging

from rag_service.chunking import chunk_text
from rag_service.embeddings import CachedEmbedder
from rag_service.store import PgVectorStore

logger = logging.getLogger(__name__)


class IngestService:
    def __init__(
        self,
        embedder: CachedEmbedder,
        store: PgVectorStore,
        chunk_size: int,
        chunk_overlap: int,
    ) -> None:
        self._embedder = embedder
        self._store = store
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    async def ingest(self, document_id: str, content: str) -> int:
        chunks = chunk_text(content, self._chunk_size, self._chunk_overlap)
        for index, chunk in enumerate(chunks):
            embedding = await self._embedder.embed(chunk)
            await self._store.add(f"{document_id}#{index}", chunk, embedding)
        logger.info("ingested %d chunks for document %s", len(chunks), document_id)
        return len(chunks)
