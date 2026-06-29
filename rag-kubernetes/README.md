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

| Méthode | Route | Auth | Rôle |
|---------|-------|------|------|
| `POST` | `/ingest` | clé API | chunk + embed + indexe (upsert idempotent) un document |
| `POST` | `/query` | clé API | question → réponse générée + sources citées |
| `DELETE` | `/documents/{id}` | clé API | supprime un document et tous ses chunks |
| `GET` | `/healthz` | public | liveness |
| `GET` | `/readyz` | public | readiness (ping PostgreSQL + Redis) |
| `GET` | `/metrics` | public | métriques Prometheus |

Les routes protégées exigent l'en-tête `X-API-Key: <API_KEY>` (comparaison en temps
constant). Les requêtes sont bornées en taille (`question` ≤ 2 000, `content` ≤ 200 000).

## Déploiement

```bash
make docker
kubectl create secret generic rag-service-secrets \
  --from-literal=DATABASE_URL=... \
  --from-literal=REDIS_URL=... \
  --from-literal=VERTEX_PROJECT=... \
  --from-literal=API_KEY=...
kubectl create configmap rag-migrations --from-file=migrations/
kubectl apply -f k8s/
```

`k8s/` fournit : `deployment` (securityContext durci, sondes liveness `/healthz` +
readiness `/readyz`), `service`, `hpa` (CPU 70 %), `pdb`, `networkpolicy` (egress
restreint à PG/Redis/HTTPS) et `migration-job` (applique `migrations/*.sql`).
`secret.example.yaml` est un gabarit — préférer `kubectl create secret`.

Voir [`TODO.md`](TODO.md) pour le reste à implémenter.
