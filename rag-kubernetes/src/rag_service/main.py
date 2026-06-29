import logging
import time
from collections.abc import Awaitable, Callable
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

import asyncpg
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from redis.asyncio import Redis

from rag_service.auth import require_api_key
from rag_service.config import Settings, load_settings
from rag_service.embeddings import CachedEmbedder
from rag_service.errors import EmbeddingError, EmptyCorpusError, GenerationError
from rag_service.ingestion import IngestService
from rag_service.logging_setup import configure_logging
from rag_service.metrics import REQUEST_LATENCY, REQUESTS
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
    store: PgVectorStore
    api_key: str


async def build_state(settings: Settings) -> AppState:
    pool = await asyncpg.create_pool(
        settings.database_url,
        min_size=settings.pool_min_size,
        max_size=settings.pool_max_size,
        command_timeout=settings.pg_command_timeout,
    )
    redis: Redis = Redis.from_url(
        settings.redis_url,
        socket_timeout=settings.redis_socket_timeout,
        socket_connect_timeout=settings.redis_socket_timeout,
    )
    backend = VertexEmbeddingBackend(
        settings.vertex_project,
        settings.vertex_location,
        settings.embedding_model,
        settings.vertex_timeout,
        settings.vertex_max_attempts,
        settings.vertex_backoff_base,
    )
    embedder = CachedEmbedder(backend, redis, settings.embedding_cache_ttl)
    store = PgVectorStore(pool)
    retriever = Retriever(embedder, store, settings.top_k)
    generator = VertexGenerator(
        settings.vertex_project,
        settings.vertex_location,
        settings.generation_model,
        settings.vertex_timeout,
        settings.vertex_max_attempts,
        settings.vertex_backoff_base,
    )
    pipeline = RagPipeline(retriever, generator)
    ingest = IngestService(embedder, store, settings.chunk_size, settings.chunk_overlap)
    return AppState(
        pool=pool,
        redis=redis,
        pipeline=pipeline,
        ingest=ingest,
        store=store,
        api_key=settings.api_key,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = load_settings()
    configure_logging(settings.log_level)
    state = await build_state(settings)
    app.state.rag = state
    try:
        yield
    finally:
        await state.pool.close()
        await state.redis.aclose()


app = FastAPI(title="rag-service", lifespan=lifespan)


@app.middleware("http")
async def track_metrics(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    start = time.perf_counter()
    response = await call_next(request)
    route = request.scope.get("route")
    path = getattr(route, "path", request.url.path)
    REQUEST_LATENCY.labels(method=request.method, path=path).observe(time.perf_counter() - start)
    REQUESTS.labels(method=request.method, path=path, status=str(response.status_code)).inc()
    return response


def get_state(request: Request) -> AppState:
    state: AppState = request.app.state.rag
    return state


@app.get("/metrics")
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
async def readyz(state: AppState = Depends(get_state)) -> dict[str, str]:
    try:
        await state.pool.fetchval("SELECT 1")
        await state.redis.ping()
    except Exception as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return {"status": "ready"}


@app.post("/query", response_model=QueryResponse, dependencies=[Depends(require_api_key)])
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


@app.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
async def ingest(
    request: IngestRequest,
    state: AppState = Depends(get_state),
) -> IngestResponse:
    try:
        chunks = await state.ingest.ingest(request.document_id, request.content)
    except EmbeddingError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    return IngestResponse(document_id=request.document_id, chunks=chunks)


@app.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_api_key)],
)
async def delete_document(
    document_id: str,
    state: AppState = Depends(get_state),
) -> dict[str, int]:
    deleted = await state.store.delete(document_id)
    return {"deleted": deleted}
