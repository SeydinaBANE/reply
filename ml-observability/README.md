# ml-observability — observabilité des modèles en production

Stack de monitoring d'un modèle servi : exposition de métriques Prometheus (latence,
débit, erreurs, coût tokens), détection de drift de données, stockage des logs de
prédiction (PostgreSQL), agrégats temps réel (Redis), visualisation Grafana.

## Architecture

```
service modèle ──► /metrics (Prometheus) ──► Grafana
        └──► predictions ──► PostgreSQL ──► job drift ──► Redis (alertes)
```

- `src/monitor/metrics.py` — registre Prometheus (compteurs, histogrammes).
- `src/monitor/drift.py` — détection de drift (PSI) entre référence et production.
- `src/monitor/store.py` — persistance des logs de prédiction (PostgreSQL).
- `grafana/dashboard.json` — dashboard prêt à importer.
- `docker-compose.yml` — Prometheus + Grafana + Postgres + Redis en local.

## Démarrage

```bash
make install
docker compose up -d        # Prometheus :9090, Grafana :3000
make test
```

Voir [`TODO.md`](TODO.md).
