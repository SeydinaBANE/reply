# TODO — llm-secure-inference

## Vault
- [ ] Implémenter `VaultClient.read_secret()` réel (hvac, KV v2)
- [ ] Cache court + invalidation, gestion de la rotation
- [ ] Auth Kubernetes (Vault Agent sidecar / k8s auth method)
- [ ] Lease renewal pour les secrets dynamiques (DB creds)

## Rate-limiting
- [ ] Finaliser le token bucket distribué (script Lua atomique Redis)
- [ ] Quotas par clé d'API / par tenant
- [ ] En-têtes `X-RateLimit-*` dans la réponse

## API & auth
- [ ] Auth Bearer + vérification de la clé contre Vault
- [ ] Endpoint `POST /v1/completions` (proxy vers backend LLM)
- [ ] Journalisation d'audit (qui, quand, quel modèle)

## Sécurité K8s
- [ ] `Deployment` : runAsNonRoot, readOnlyRootFilesystem, drop capabilities
- [ ] `Role` + `RoleBinding` minimalistes
- [ ] NetworkPolicy egress restreint
- [ ] Annotations Vault Agent Injector

## Tests
- [ ] `test_ratelimit_allows_under_quota`
- [ ] `test_ratelimit_blocks_over_quota`
- [ ] `test_vault_missing_secret_raises`
