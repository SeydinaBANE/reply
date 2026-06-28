import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

import asyncpg
from fastapi import Depends, FastAPI, HTTPException, Request, status
from redis.asyncio import Redis

from rag_service.config import Settings, load_settings
from rag_service.embeddings import CachedEmbedder
from rag_service.errors import EmbeddingError, EmptyCorpusError, GenerationError
from rag_service.ingestion import IngestService
from rag_service.models import IngestRequest, IngestResponse, QueryRequest, QueryResponse
from rag_service.pipeline import RagPipeline
from rag_service.retrieval import Retriever
from rag_service.store import PgVectorStore
from rag_service.vertex import VertexEmbeddingBackend, VertexGenerator

logger = logging.getLogger(__name__)


@dataclass
class AppState:
    pool: asyncpg.Pool
    redis: Redis
    pipeline: RagPipeline
    ingest: IngestService


async def build_state(settings: Settings) -> AppState:
    pool = await asyncpg.create_pool(
        settings.database_url,
        min_size=settings.pool_min_size,
        max_size=settings.pool_max_size,
    )
    redis: Redis = Redis.from_url(settings.redis_url)
    backend = VertexEmbeddingBackend(
        settings.vertex_project, settings.vertex_location, settings.embedding_model
    )
    embedder = CachedEmbedder(backend, redis, settings.embedding_cache_ttl)
    store = PgVectorStore(pool)
    retriever = Retriever(embedder, store, settings.top_k)
    generator = VertexGenerator(
        settings.vertex_project, settings.vertex_location, settings.generation_model
    )
    pipeline = RagPipeline(retriever, generator)
    ingest = IngestService(embedder, store, settings.chunk_size, settings.chunk_overlap)
    return AppState(pool=pool, redis=redis, pipeline=pipeline, ingest=ingest)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    state = await build_state(load_settings())
    app.state.rag = state
    try:
        yield
    finally:
        await state.pool.close()
        await state.redis.aclose()


app = FastAPI(title="rag-service", lifespan=lifespan)


def get_state(request: Request) -> AppState:
    state: AppState = request.app.state.rag
    return state


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
async def readyz(state: AppState = Depends(get_state)) -> dict[str, str]:
    await state.pool.fetchval("SELECT 1")
    return {"status": "ready"}


@app.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    state: AppState = Depends(get_state),
) -> QueryResponse:
    try:
        return await state.pipeline.answer(request.question, request.top_k)
    except EmptyCorpusError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except (EmbeddingError, GenerationError) as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@app.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest(
    request: IngestRequest,
    state: AppState = Depends(get_state),
) -> IngestResponse:
    try:
        chunks = await state.ingest.ingest(request.document_id, request.content)
    except EmbeddingError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return IngestResponse(document_id=request.document_id, chunks=chunks)
