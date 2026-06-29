from rag_service.models import Passage


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, bytes] = {}

    async def get(self, key: str) -> bytes | None:
        return self.store.get(key)

    async def set(self, key: str, value: bytes, ex: int | None = None) -> None:
        self.store[key] = value


class FakeEmbedder:
    def __init__(self, calls: list[str] | None = None) -> None:
        self.calls = calls if calls is not None else []

    async def embed(self, text: str) -> list[float]:
        self.calls.append(text)
        return [float(len(text)), 0.0, 1.0]


class FakeStore:
    def __init__(self, passages: list[Passage] | None = None) -> None:
        self.passages = passages if passages is not None else []
        self.added: list[tuple[str, str, list[float]]] = []

    async def add(self, document_id: str, content: str, embedding: list[float]) -> None:
        self.added.append((document_id, content, embedding))

    async def search(self, embedding: list[float], top_k: int) -> list[Passage]:
        return self.passages[:top_k]

    async def count(self) -> int:
        return len(self.passages)

    async def delete(self, document_id: str) -> int:
        return 1


class FakeGenerator:
    def __init__(self, answer: str = "generated answer") -> None:
        self.answer = answer
        self.prompts: list[str] = []

    async def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.answer
