import pytest

from rag_service.store import PgVectorStore, format_vector


class _FakePool:
    def __init__(self) -> None:
        self.rows: dict[str, tuple[str, str]] = {}
        self.queries: list[str] = []

    async def execute(self, query: str, *args: object) -> str:
        self.queries.append(query)
        if "INSERT" in query:
            document_id, content, embedding = args
            self.rows[str(document_id)] = (str(content), str(embedding))
            return "INSERT 0 1"
        if "DELETE" in query:
            base = str(args[0])
            removed = [k for k in self.rows if k == base or k.startswith(f"{base}#")]
            for key in removed:
                del self.rows[key]
            return f"DELETE {len(removed)}"
        return "OK"


def test_format_vector_formats_list() -> None:
    assert format_vector([1.0, 2.5]) == "[1.0,2.5]"


@pytest.mark.asyncio
async def test_add_upserts_same_document_id() -> None:
    pool = _FakePool()
    store = PgVectorStore(pool)  # type: ignore[arg-type]
    await store.add("doc#0", "first", [1.0])
    await store.add("doc#0", "second", [2.0])
    assert len(pool.rows) == 1
    assert pool.rows["doc#0"][0] == "second"
    assert "ON CONFLICT" in pool.queries[0]


@pytest.mark.asyncio
async def test_delete_removes_all_chunks_of_document() -> None:
    pool = _FakePool()
    store = PgVectorStore(pool)  # type: ignore[arg-type]
    await store.add("doc#0", "a", [1.0])
    await store.add("doc#1", "b", [2.0])
    await store.add("other#0", "c", [3.0])
    deleted = await store.delete("doc")
    assert deleted == 2
    assert set(pool.rows) == {"other#0"}
