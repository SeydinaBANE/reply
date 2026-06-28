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

- `src/rag_service/main.py` — couche API (FastAPI), traduit les erreurs domaine en HTTP.
- `src/rag_service/retrieval.py` — couche domaine : recherche des passages pertinents.
- `src/rag_service/embeddings.py` — adaptateur Vertex AI + cache Redis.
- `src/rag_service/config.py` — configuration via `pydantic-settings`.

## Démarrage

```bash
make install
cp .env.example .env   # renseigner VERTEX_PROJECT, DATABASE_URL, REDIS_URL
make test
make run               # uvicorn sur :8000
```

## Déploiement

```bash
make docker
kubectl apply -f k8s/
```

Voir [`TODO.md`](TODO.md) pour le reste à implémenter.
