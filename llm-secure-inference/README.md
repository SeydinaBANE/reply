# llm-secure-inference — service d'inférence LLM sécurisé

API d'inférence LLM avec gestion centralisée des secrets (HashiCorp Vault), authentification,
quotas et rate-limiting (Redis), durcissement Kubernetes (RBAC, secrets, contexte non-root).

## Architecture

```
client ──► FastAPI (auth) ──► RateLimiter (Redis) ──► LLM backend
                  └──► VaultClient (clés API, rotation)
```

- `src/inference/vault_client.py` — lecture des secrets KV + cache court.
- `src/inference/ratelimit.py` — token bucket distribué (Redis).
- `src/inference/main.py` — API, auth Bearer, traduction des erreurs domaine.
- `k8s/` — Deployment non-root, RBAC, ServiceAccount, Vault Agent annotations.

## Démarrage

```bash
make install
cp .env.example .env       # VAULT_ADDR, VAULT_TOKEN, REDIS_URL
make test
make run
```

Voir [`TODO.md`](TODO.md).
