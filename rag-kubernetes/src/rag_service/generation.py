from typing import Protocol

from rag_service.models import Passage

_SYSTEM_INSTRUCTION = (
    "Answer the question using only the provided context. "
    "If the context is insufficient, say so. Cite sources by their [n] marker."
)


class Generator(Protocol):
    async def generate(self, prompt: str) -> str: ...


def build_prompt(question: str, passages: list[Passage]) -> str:
    context = "\n\n".join(
        f"[{index}] {passage.content}" for index, passage in enumerate(passages, start=1)
    )
    return f"{_SYSTEM_INSTRUCTION}\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
