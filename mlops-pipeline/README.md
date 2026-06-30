# mlops-pipeline — train → registry → deploy

Pipeline d'industrialisation d'un modèle ML : entraînement reproductible, suivi des
expériences (MLflow), publication des artefacts sur JFrog Artifactory, packaging Docker,
orchestration via Vertex AI Pipelines, déploiement Kubernetes — le tout piloté par CI/CD (GitHub Actions).

## Flux

```
CI (GitHub Actions) ──► train (MLflow tracking) ──► artifact (JFrog) ──► image (Docker)
                                                                               └──► deploy (K8s)
```

- `src/pipeline/dataset.py` — chargement + validation du dataset (CSV → features/labels).
- `src/pipeline/train.py` — entraînement (LogisticRegression) + métriques + sérialisation.
- `src/pipeline/evaluation.py` — gate d'évaluation (seuil d'accuracy).
- `src/pipeline/tracker.py` — `ExperimentTracker` (Protocol) + adaptateurs MLflow / NoOp.
- `src/pipeline/registry.py` — publication/récupération de l'artefact modèle (JFrog).
- `src/pipeline/runner.py` — orchestration train → log → save → push → gate.
- `src/pipeline/__main__.py` — entrée CLI (`python -m pipeline`).
- `src/pipeline/config.py` — configuration via `pydantic-settings`.
- `vertex/pipeline.py` — définition du DAG Vertex AI Pipelines.

## Démarrage

```bash
make install
cp .env.example .env
make test
python -m pipeline --data data/train.csv --label-column label
```

Voir [`TODO.md`](TODO.md).
