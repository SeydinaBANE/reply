# llm-secure-inference — service d'inférence LLM sécurisé

API d'inférence LLM avec gestion centralisée des secrets (HashiCorp Vault), authentification,
quotas et rate-limiting (Redis), observabilité Prometheus et durcissement Kubernetes
(RBAC, NetworkPolicy, contexte non-root).

## Architecture

```
client ──► FastAPI (auth) ──► RateLimiter (Redis, Lua atomique) ──► LLM backend (vLLM | Vertex)
                  └──► VaultClient (token | k8s auth) — clés API rafraîchies (TTL)
```

- `src/inference/vault_client.py` — `VaultClient`, `HvacSecretReader` (token) et
  `KubernetesAuthReader` (k8s auth method) ; erreurs Vault distinguées (auth / indispo / absent).
- `src/inference/auth.py` — `ApiKeyAuthenticator` (comparaison timing-safe `hmac.compare_digest`)
  + `ApiKeyProvider` (rotation des clés depuis Vault sur TTL).
- `src/inference/ratelimit.py` — compteur distribué par clé via script Lua atomique ;
  **fail-open + alerte** si Redis est indisponible.
- `src/inference/backend.py` — `LlmBackend` (Protocol), `EchoBackend`, `VllmBackend`,
  `VertexBackend`, factory `build_backend` ; chaque appel borné par un timeout.
- `src/inference/audit.py` — journal d'audit JSON structuré (clé masquée, horodaté).
- `src/inference/metrics.py` + `instrumentation.py` — métriques Prometheus + middleware latence.
- `src/inference/service.py` — orchestration auth → rate-limit → backend → audit.
- `src/inference/main.py` — API : `/v1/completions`, `/healthz`, `/readyz`, `/metrics`.
- `k8s/` — Deployment durci, RBAC, Service, NetworkPolicy, PDB, HPA, ServiceMonitor,
  annotations Vault Agent.
- [`RUNBOOK.md`](RUNBOOK.md) — métriques clés et playbook d'incidents.

## Configuration

Variables principales (voir `.env.example`) :

- `BACKEND` = `echo` (défaut, dev/tests) | `vllm` (HTTP OpenAI-compatible) | `vertex`.
  `BACKEND_URL`, `BACKEND_MODEL`, `BACKEND_TIMEOUT_S` ; pour Vertex, `VERTEX_PROJECT` /
  `VERTEX_LOCATION` et l'extra `pip install ".[vertex]"`.
- `VAULT_AUTH` = `token` (dev, `VAULT_TOKEN`) | `kubernetes` (prod, `VAULT_ROLE`).
- `API_KEY_REFRESH_S` — période de rafraîchissement des clés depuis Vault.
- `RATE_LIMIT_PER_MINUTE`, `RATE_LIMIT_FAIL_OPEN` (défaut `true`).
- `REDIS_URL` (utiliser `rediss://` + auth en prod), `REDIS_SOCKET_TIMEOUT`.

## Démarrage

```bash
make install
cp .env.example .env        # VAULT_ADDR, VAULT_TOKEN, REDIS_URL, BACKEND…
make test                   # tests unitaires (l'intégration est exclue par défaut)
make run                    # uvicorn sur :8000
```

### Tests d'intégration

Nécessitent Docker (testcontainers Redis + Vault dev) :

```bash
pytest -m integration
```

Voir [`TODO.md`](TODO.md) pour le reste à faire.
