# TODO — ml-observability

## Métriques
- [x] Histogramme de latence + compteur d'erreurs (`observe_request`)
- [x] Métrique de coût tokens LLM (`add_tokens`)
- [x] Middleware FastAPI d'instrumentation (latence HTTP par route)

## Drift
- [x] `population_stability_index()` + tests numériques
- [x] Classification en niveaux (`classify_drift`) + `evaluate_drift` multi-feature
- [x] Publication d'alertes Redis quand seuil dépassé (`AlertPublisher`)
- [ ] Job périodique : comparer fenêtre prod (store) vs jeu de référence
- [ ] Drift de concept (suivi de la métrique cible si labels disponibles)

## Stockage
- [x] Schéma PostgreSQL `predictions` + `record` / `recent_features`
- [ ] Rétention / partitionnement par jour

## Visualisation
- [x] `grafana/dashboard.json` (latence, erreurs, tokens)
- [ ] Provisioning automatique datasource Prometheus
- [ ] Règles d'alerte Grafana

## Tests
- [x] PSI, classification, evaluate_drift, store, alerts, endpoints API
- [ ] Job de drift périodique de bout en bout
