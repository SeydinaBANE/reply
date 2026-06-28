def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    if size <= 0:
        raise ValueError("size must be positive")
    if overlap < 0 or overlap >= size:
        raise ValueError("overlap must be in [0, size)")

    normalized = " ".join(text.split())
    if not normalized:
        return []

    step = size - overlap
    chunks: list[str] = []
    for start in range(0, len(normalized), step):
        chunk = normalized[start : start + size]
        if chunk:
            chunks.append(chunk)
        if start + size >= len(normalized):
            break
    return chunks
