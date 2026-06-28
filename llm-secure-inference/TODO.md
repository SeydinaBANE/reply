# TODO — llm-secure-inference

## Vault
- [x] `HvacSecretReader` (KV v2) + `VaultClient.read_secret`
- [x] Chargement des clés API autorisées depuis Vault au démarrage
- [ ] Cache court + invalidation, gestion de la rotation
- [ ] Auth Kubernetes (Vault Agent sidecar / k8s auth method)
- [ ] Lease renewal pour les secrets dynamiques (DB creds)

## Rate-limiting
- [x] Compteur distribué par clé d'API (Redis) avec quota/minute
- [x] En-tête `X-RateLimit-Remaining` dans la réponse
- [ ] Token bucket atomique (script Lua) pour la précision sous forte charge
- [ ] Quotas différenciés par tenant

## API & auth
- [x] Auth Bearer + vérification de la clé (`ApiKeyAuthenticator`)
- [x] Endpoint `POST /v1/completions` (backend abstrait)
- [x] Journalisation d'audit (clé masquée)
- [ ] Backend LLM réel (Vertex/vLLM) derrière `LlmBackend`

## Sécurité K8s
- [x] `Deployment` durci (runAsNonRoot, readOnlyRootFilesystem, drop caps)
- [x] `Role` + `RoleBinding` minimalistes
- [ ] NetworkPolicy egress restreint

## Tests
- [x] auth, rate-limit, backend, service, endpoints API (14 tests)
- [ ] Test d'intégration contre un Vault de dev (testcontainers)
