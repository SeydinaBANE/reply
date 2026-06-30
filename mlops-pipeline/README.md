# mlops-pipeline — train → registry → deploy

Pipeline d'industrialisation d'un modèle ML : entraînement reproductible, suivi des
expériences (MLflow), publication des artefacts sur JFrog Artifactory, packaging Docker,
orchestration via Vertex AI Pipelines, déploiement Kubernetes — le tout piloté par GitLab CI/CD.

## Flux

```
GitLab CI ──► train (MLflow tracking) ──► artifact (JFrog) ──► image (Docker)
                                                                   └──► deploy (K8s)
```

- `src/pipeline/dataset.py` — chargement + validation pandera (types, nulls, équilibre des classes) + hash déterministe du dataset.
- `src/pipeline/train.py` — entraînement (LogisticRegression) avec `stratify`, f1 binaire/macro selon le nombre de classes.
- `src/pipeline/evaluation.py` — gate d'évaluation : seuil d'accuracy **+ comparaison à une baseline** (avec tolérance).
- `src/pipeline/tracker.py` — `ExperimentTracker` (Protocol) + adaptateurs MLflow / NoOp ; run géré (context manager), `log_model` avec signature.
- `src/pipeline/registry.py` — push/pull JFrog en **streaming** avec **retry/backoff** et timeouts.
- `src/pipeline/runner.py` — orchestration train → log params/metrics → **gate → save → log_model → push** (le gate bloque la publication).
- `src/pipeline/__main__.py` — entrée CLI (`python -m pipeline`).
- `src/pipeline/config.py` — configuration via `pydantic-settings`.
- `vertex/pipeline.py` — spec DAG Vertex (composants train → evaluate → register → deploy, dépendances validées).

> **Gate :** le seuil d'accuracy **et** la non-régression vs baseline sont vérifiés
> **avant** toute sérialisation/publication. Un modèle recalé n'est jamais poussé sur JFrog.

## Démarrage

```bash
make install
cp .env.example .env
make test
python -m pipeline --data data/sample.csv --label-column label
```

Les secrets (`JFROG_TOKEN`, credentials kube) doivent provenir de variables CI
masquées/protégées ou de Vault — jamais en clair. Le `deploy-staging` GitLab attend
le `rollout status`, lance un smoke test `/healthz`, et **rollback** en cas d'échec.

Voir [`TODO.md`](TODO.md).
