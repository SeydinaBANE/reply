import os
from pathlib import Path

import asyncpg
import pytest

from rag_service.store import PgVectorStore

pytestmark = pytest.mark.integration

_TEST_DB = os.getenv("TEST_DATABASE_URL")
_MIGRATIONS = Path(__file__).resolve().parent.parent / "migrations"


@pytest.mark.skipif(_TEST_DB is None, reason="TEST_DATABASE_URL not set")
@pytest.mark.asyncio
async def test_add_then_search_roundtrip() -> None:
    pool = await asyncpg.create_pool(_TEST_DB)
    assert pool is not None
    try:
        for sql_file in sorted(_MIGRATIONS.glob("*.sql")):
            await pool.execute(sql_file.read_text())
        await pool.execute("TRUNCATE documents")
        store = PgVectorStore(pool)
        await store.add("doc#0", "the sky is blue", [0.1] * 768)
        results = await store.search([0.1] * 768, top_k=1)
        assert results[0].document_id == "doc#0"
        assert await store.count() == 1
    finally:
        await pool.close()
