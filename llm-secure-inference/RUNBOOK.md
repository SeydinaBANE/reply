# Runbook — llm-secure-inference

## Endpoints

- `GET /healthz` — liveness (process up). Used by the liveness/startup probes.
- `GET /readyz` — readiness; checks Redis + Vault. Returns 503 if a dependency is down.
- `GET /metrics` — Prometheus exposition.

## Key metrics

| Metric | Meaning |
|--------|---------|
| `http_request_latency_seconds{method,path}` | API latency histogram |
| `inference_tokens_total` | Tokens returned to clients |
| `inference_auth_failures_total` | Rejected API keys (401) |
| `inference_rate_limited_total` | Requests blocked by the quota (429) |
| `inference_backend_errors_total` | LLM backend failures (502) |
| `ratelimit_redis_failures_total` | Rate-limiter Redis failures (fail-open events) |

## Incident playbook

### `ratelimit_redis_failures_total` rising
Redis is unreachable. The limiter is **failing open** (requests still served, no quota
enforced). Check Redis connectivity and `REDIS_URL`. Quotas resume automatically once Redis
recovers. To prioritise quota enforcement over availability set `RATE_LIMIT_FAIL_OPEN=false`
(requests then return 503 while Redis is down).

### `/readyz` returning 503
A dependency check failed. `detail=redis unavailable` → Redis down; `detail=vault unavailable`
→ Vault unreachable or token/role invalid. Pods are pulled from the Service until ready.

### `inference_backend_errors_total` spiking / high latency
The LLM backend is slow or erroring. Each call is bounded by `BACKEND_TIMEOUT_S`; timeouts
surface as 502. Check the vLLM/Vertex backend health and `BACKEND_URL`.

### Spike in `inference_auth_failures_total`
Possible credential scan or a key rotation that did not propagate. Keys refresh from Vault
every `API_KEY_REFRESH_S` seconds; confirm the Vault secret `api_keys` is current.
