import logging

import asyncpg

from rag_service.models import Passage

logger = logging.getLogger(__name__)


def format_vector(embedding: list[float]) -> str:
    return "[" + ",".join(repr(value) for value in embedding) + "]"


class PgVectorStore:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def add(self, document_id: str, content: str, embedding: list[float]) -> None:
        await self._pool.execute(
            "INSERT INTO documents (document_id, content, embedding) VALUES ($1, $2, $3)",
            document_id,
            content,
            format_vector(embedding),
        )

    async def search(self, embedding: list[float], top_k: int) -> list[Passage]:
        rows = await self._pool.fetch(
            """
            SELECT document_id, content, 1 - (embedding <=> $1) AS score
            FROM documents
            ORDER BY embedding <=> $1
            LIMIT $2
            """,
            format_vector(embedding),
            top_k,
        )
        return [
            Passage(document_id=row["document_id"], content=row["content"], score=row["score"])
            for row in rows
        ]

    async def count(self) -> int:
        result = await self._pool.fetchval("SELECT COUNT(*) FROM documents")
        return int(result)
