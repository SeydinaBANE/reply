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
- [ ] Script d'application des migrations au démarrage

## Infra
- [x] `k8s/deployment.yaml` (resources, liveness/readiness probes)
- [x] CI GitHub Actions : lint → typecheck → test
- [ ] `Secret` K8s pour DATABASE_URL / credentials Vertex
- [ ] HorizontalPodAutoscaler sur la CPU

## Tests
- [x] `test_retrieve_empty_corpus`, `test_retrieve_returns_top_k`
- [x] Chunking, cache embeddings, pipeline, ingestion
- [x] Endpoints API (`/query`, `/ingest`) via TestClient + overrides
- [ ] Tests d'intégration store contre une vraie base pgvector
