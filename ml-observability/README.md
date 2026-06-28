# ml-observability — observabilité des modèles en production

Stack de monitoring d'un modèle servi : exposition de métriques Prometheus (latence,
débit, erreurs, coût tokens), détection de drift de données, stockage des logs de
prédiction (PostgreSQL), agrégats temps réel (Redis), visualisation Grafana.

## Architecture

```
service modèle ──► /metrics (Prometheus) ──► Grafana
        └──► predictions ──► PostgreSQL ──► job drift ──► Redis (alertes)
```

- `src/monitor/metrics.py` — registre Prometheus (latence, erreurs, tokens) + helpers.
- `src/monitor/instrumentation.py` — middleware FastAPI (latence HTTP par route).
- `src/monitor/drift.py` — PSI + classification en niveaux d'alerte.
- `src/monitor/monitoring.py` — `evaluate_drift` (PSI par feature, pire cas).
- `src/monitor/store.py` — persistance des prédictions (PostgreSQL / JSONB).
- `src/monitor/alerts.py` — publication des alertes de drift (Redis pub/sub).
- `src/monitor/main.py` — API : `/log`, `/drift`, `/metrics`, `/healthz`, `/readyz`.
- `migrations/001_init.sql` — table `predictions`.
- `grafana/dashboard.json` — dashboard prêt à importer.
- `docker-compose.yml` — Prometheus + Grafana + Postgres + Redis en local.

## Démarrage

```bash
make install
docker compose up -d        # Prometheus :9090, Grafana :3000
make test
```

Voir [`TODO.md`](TODO.md).
