# TODO — llm-secure-inference

## Vault
- [x] `HvacSecretReader` (KV v2) + `VaultClient.read_secret`
- [x] Chargement des clés API autorisées depuis Vault au démarrage
- [x] Cache court + invalidation, gestion de la rotation (`ApiKeyProvider`, TTL)
- [x] Auth Kubernetes (k8s auth method) — `KubernetesAuthReader`
- [ ] Lease renewal pour les secrets dynamiques (DB creds)

## Rate-limiting
- [x] Compteur distribué par clé d'API (Redis) avec quota/minute
- [x] En-tête `X-RateLimit-Remaining` dans la réponse
- [x] Token bucket atomique (script Lua) + fail-open sur panne Redis
- [ ] Quotas différenciés par tenant

## API & auth
- [x] Auth Bearer + vérification de la clé (`ApiKeyAuthenticator`, timing-safe)
- [x] Endpoint `POST /v1/completions` (backend abstrait)
- [x] Journalisation d'audit JSON structurée (clé masquée)
- [x] Backend LLM réel (vLLM + Vertex) derrière `LlmBackend` + timeout
- [ ] Streaming (`/v1/completions` SSE)

## Observabilité
- [x] Métriques Prometheus + endpoint `/metrics`
- [x] Probes `/healthz` (liveness) et `/readyz` (Redis + Vault)
- [x] Runbook d'incidents (`RUNBOOK.md`)
- [ ] Tracing OpenTelemetry (extra optionnel)

## Sécurité K8s
- [x] `Deployment` durci (runAsNonRoot, readOnlyRootFilesystem, drop caps, seccomp)
- [x] `Role` + `RoleBinding` minimalistes
- [x] NetworkPolicy egress restreint (DNS / Redis / Vault / backend)
- [x] PodDisruptionBudget, HPA, Service, ServiceMonitor
- [x] Image multi-stage + HEALTHCHECK

## Tests
- [x] auth, rate-limit, backend, service, endpoints API (incl. 429/502)
- [x] Tests d'intégration testcontainers (Vault dev + Redis), marqueur `integration`
- [ ] Charge / soak (k6) sous quota et fail-open
