import logging

from rag_service.generation import Generator, build_prompt
from rag_service.models import QueryResponse
from rag_service.retrieval import Retriever

logger = logging.getLogger(__name__)


class RagPipeline:
    def __init__(self, retriever: Retriever, generator: Generator) -> None:
        self._retriever = retriever
        self._generator = generator

    async def answer(self, question: str, top_k: int | None = None) -> QueryResponse:
        passages = await self._retriever.retrieve(question, top_k)
        prompt = build_prompt(question, passages)
        answer = await self._generator.generate(prompt)
        logger.info("generated answer from %d passages", len(passages))
        return QueryResponse(answer=answer, sources=passages)
