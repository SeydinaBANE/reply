from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Completion:
    text: str
    tokens: int


class LlmBackend(Protocol):
    async def complete(self, prompt: str, max_tokens: int) -> Completion: ...


class EchoBackend:
    async def complete(self, prompt: str, max_tokens: int) -> Completion:
        words = prompt.split()[:max_tokens]
        return Completion(text=" ".join(words), tokens=len(words))
