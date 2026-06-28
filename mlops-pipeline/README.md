# mlops-pipeline — train → registry → deploy

Pipeline d'industrialisation d'un modèle ML : entraînement reproductible, suivi des
expériences (MLflow), publication des artefacts sur JFrog Artifactory, packaging Docker,
orchestration via Vertex AI Pipelines, déploiement Kubernetes — le tout piloté par GitLab CI/CD.

## Flux

```
GitLab CI ──► train (MLflow tracking) ──► artifact (JFrog) ──► image (Docker)
                                                                   └──► deploy (K8s)
```

- `src/pipeline/train.py` — entraînement + log des métriques/params/artefact.
- `src/pipeline/registry.py` — publication/récupération de l'artefact modèle (JFrog).
- `src/pipeline/config.py` — configuration via `pydantic-settings`.
- `vertex/pipeline.py` — définition du DAG Vertex AI Pipelines.

## Démarrage

```bash
make install
cp .env.example .env
make test
python -m pipeline.train --data data/train.csv
```

Voir [`TODO.md`](TODO.md).
