import pytest

from rag_service.chunking import chunk_text


def test_chunk_text_empty_returns_no_chunks() -> None:
    assert chunk_text("   ", size=100, overlap=10) == []


def test_chunk_text_respects_size_and_overlap() -> None:
    text = "a " * 500
    chunks = chunk_text(text, size=100, overlap=20)
    assert all(len(chunk) <= 100 for chunk in chunks)
    assert len(chunks) > 1


def test_chunk_text_invalid_overlap_raises() -> None:
    with pytest.raises(ValueError):
        chunk_text("hello world", size=10, overlap=10)
