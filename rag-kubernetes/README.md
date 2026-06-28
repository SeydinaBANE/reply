# rag-kubernetes — RAG d'entreprise sur Kubernetes

API de questions/réponses sur une base documentaire interne. Récupération sémantique
(pgvector), cache des embeddings et des sessions (Redis), génération via Vertex AI,
servie en conteneur sur Kubernetes.

## Architecture

```
client ──► FastAPI ──► Retriever ──► pgvector (PostgreSQL)
                │           └──────► Redis (cache embeddings)
                └──────► Vertex AI (embeddings + LLM)
```

- `src/rag_service/main.py` — couche API (FastAPI) : lifespan, DI, endpoints `/query`, `/ingest`, `/healthz`, `/readyz` ; traduit les erreurs domaine en HTTP.
- `src/rag_service/pipeline.py` — orchestration RAG : retrieve → prompt → génération.
- `src/rag_service/retrieval.py` — couche domaine : recherche des passages pertinents.
- `src/rag_service/store.py` — `PgVectorStore` (asyncpg + pgvector) : `add` / `search` / `count`.
- `src/rag_service/embeddings.py` — cache Redis des embeddings.
- `src/rag_service/vertex.py` — adaptateurs Vertex AI (embeddings + génération, imports lazy).
- `src/rag_service/ingestion.py` — chunking + indexation des documents.
- `src/rag_service/config.py` — configuration via `pydantic-settings`.
- `migrations/001_init.sql` — extension `vector`, table `documents`, index HNSW cosine.

## Démarrage

```bash
make install
cp .env.example .env   # renseigner VERTEX_PROJECT, DATABASE_URL, REDIS_URL
psql "$DATABASE_URL" -f migrations/001_init.sql
make test
make run               # uvicorn sur :8000
```

### Endpoints

| Méthode | Route | Rôle |
|---------|-------|------|
| `POST` | `/ingest` | chunk + embed + indexe un document |
| `POST` | `/query` | question → réponse générée + sources citées |
| `GET` | `/healthz` | liveness |
| `GET` | `/readyz` | readiness (ping PostgreSQL) |

## Déploiement

```bash
make docker
kubectl apply -f k8s/
```

Voir [`TODO.md`](TODO.md) pour le reste à implémenter.
