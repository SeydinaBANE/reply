# TODO — rag-kubernetes

## Domaine / Retrieval
- [x] Implémenter `Retriever.retrieve()` (pgvector cosine via `PgVectorStore.search`)
- [x] Chunking des documents (taille + overlap configurables)
- [x] Gestion du cas corpus vide (lève `EmptyCorpusError`)
- [ ] Re-ranking optionnel des passages récupérés

## Embeddings
- [x] Adaptateur Vertex AI `text-embedding` (`VertexEmbeddingBackend`, import lazy)
- [x] Cache Redis : clé = hash(texte), TTL configurable
- [ ] Batch des appels d'embedding

## API
- [x] Endpoint `POST /query` : question → réponse + sources citées
- [x] Endpoint `POST /ingest` : indexation de documents
- [x] Endpoints `GET /healthz` et `GET /readyz`
- [ ] Streaming de la réponse LLM (SSE)

## Données
- [x] Migration SQL : extension `vector`, table `documents`
- [x] Index HNSW cosine sur la colonne embedding
- [x] Ingestion idempotente (index unique + upsert `ON CONFLICT`)
- [x] Job K8s d'application des migrations au démarrage

## Sécurité / Fiabilité
- [x] Authentification par clé API (`X-API-Key`)
- [x] Appels Vertex non bloquants (`run_in_executor`) + client initialisé une fois
- [x] Timeouts + retries Vertex, timeouts PG/Redis, cache dégradé gracieusement
- [x] Limites de taille des entrées
- [x] Logging structuré + endpoint `/metrics` Prometheus

## Infra
- [x] `k8s/deployment.yaml` (resources, liveness/readiness probes, securityContext)
- [x] Pipeline GitLab : lint → typecheck → test → build
- [x] `Secret` K8s pour DATABASE_URL / credentials Vertex (gabarit + `kubectl create`)
- [x] HorizontalPodAutoscaler sur la CPU, PodDisruptionBudget, NetworkPolicy

## Tests
- [x] `test_retrieve_empty_corpus`, `test_retrieve_returns_top_k`
- [x] Chunking, cache embeddings, pipeline, ingestion
- [x] Endpoints API (`/query`, `/ingest`, `/documents/{id}`) + auth + limites de taille
- [x] Vertex (non bloquant, retries), store (upsert/delete)
- [x] Tests d'intégration store contre une vraie base pgvector (marqués `integration`)
