# TODO — ml-observability

## Métriques
- [ ] Exposer histogramme de latence + compteur d'erreurs sur `/metrics`
- [ ] Métrique de coût tokens LLM (compteur par modèle)
- [ ] Middleware FastAPI d'instrumentation automatique

## Drift
- [ ] Implémenter `population_stability_index()` (déjà esquissé) + tests numériques
- [ ] Job périodique : comparer fenêtre prod vs jeu de référence
- [ ] Seuils d'alerte (PSI > 0.2 = warning, > 0.25 = critique) → Redis pub/sub
- [ ] Drift de concept (suivi de la métrique cible si labels disponibles)

## Stockage
- [ ] Schéma PostgreSQL `predictions(id, ts, features jsonb, prediction, latency_ms)`
- [ ] Rétention / partitionnement par jour

## Visualisation
- [ ] Compléter `grafana/dashboard.json` (panels latence p50/p95/p99, erreurs, drift)
- [ ] Provisioning automatique datasource Prometheus
- [ ] Règles d'alerte Grafana

## Tests
- [ ] `test_psi_identical_distributions_is_zero`
- [ ] `test_psi_detects_shift`
