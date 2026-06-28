import logging

from fastapi import Depends, FastAPI, HTTPException, status

from rag_service.errors import EmptyCorpusError
from rag_service.models import QueryRequest, QueryResponse
from rag_service.retrieval import Retriever

logger = logging.getLogger(__name__)

app = FastAPI(title="rag-service")


def get_retriever() -> Retriever:
    raise NotImplementedError("wire Retriever via lifespan / dependency override")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    retriever: Retriever = Depends(get_retriever),
) -> QueryResponse:
    try:
        passages = await retriever.retrieve(request.question, request.top_k)
    except EmptyCorpusError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    answer = passages[0].content if passages else ""
    return QueryResponse(answer=answer, sources=passages)
