# llm-secure-inference — service d'inférence LLM sécurisé

API d'inférence LLM avec gestion centralisée des secrets (HashiCorp Vault), authentification,
quotas et rate-limiting (Redis), durcissement Kubernetes (RBAC, secrets, contexte non-root).

## Architecture

```
client ──► FastAPI (auth) ──► RateLimiter (Redis) ──► LLM backend
                  └──► VaultClient (clés API, rotation)
```

- `src/inference/vault_client.py` — `VaultClient` + `HvacSecretReader` (lecture KV v2).
- `src/inference/auth.py` — `ApiKeyAuthenticator` (clés chargées depuis Vault au démarrage).
- `src/inference/ratelimit.py` — compteur distribué par clé (Redis).
- `src/inference/backend.py` — `LlmBackend` (Protocol) + `EchoBackend`.
- `src/inference/audit.py` — journal d'audit (clé masquée).
- `src/inference/service.py` — orchestration auth → rate-limit → backend → audit.
- `src/inference/main.py` — API : auth Bearer, `/v1/completions`, `/healthz`, `/readyz`.
- `k8s/` — Deployment non-root, RBAC, ServiceAccount, Vault Agent annotations.

## Démarrage

```bash
make install
cp .env.example .env       # VAULT_ADDR, VAULT_TOKEN, REDIS_URL
make test
make run
```

Voir [`TODO.md`](TODO.md).
