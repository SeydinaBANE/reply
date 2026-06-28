# TODO — rag-kubernetes

## Domaine / Retrieval
- [ ] Implémenter `Retriever.retrieve()` : requête pgvector `ORDER BY embedding <=> $1 LIMIT k`
- [ ] Chunking des documents (taille + overlap configurables)
- [ ] Re-ranking optionnel des passages récupérés
- [ ] Gestion du cas corpus vide (lève `EmptyCorpusError`)

## Embeddings
- [ ] Adaptateur Vertex AI `text-embedding` réel (actuellement stub)
- [ ] Cache Redis : clé = hash(texte), TTL configurable
- [ ] Batch des appels d'embedding

## API
- [ ] Endpoint `POST /query` : question → réponse + sources citées
- [ ] Endpoint `POST /ingest` : upload + indexation de documents
- [ ] Endpoint `GET /healthz` et `GET /readyz`
- [ ] Streaming de la réponse LLM (SSE)

## Données
- [ ] Migration SQL : extension `vector`, table `documents(id, content, embedding vector)`
- [ ] Index ivfflat / hnsw sur la colonne embedding

## Infra
- [ ] Compléter `k8s/deployment.yaml` (resources, liveness/readiness probes)
- [ ] `Secret` K8s pour DATABASE_URL / credentials Vertex
- [ ] HorizontalPodAutoscaler sur la CPU
- [ ] Pipeline GitLab : lint → typecheck → test → build → push

## Tests
- [ ] `test_retrieve_empty_corpus` (déjà esquissé)
- [ ] `test_retrieve_returns_top_k`
- [ ] `test_query_endpoint_cites_sources` (TestClient + mocks)
