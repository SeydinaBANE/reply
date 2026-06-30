# TODO — mlops-pipeline

## Entraînement
- [x] Implémenter `train_model()` (LogisticRegression + StandardScaler) avec split train/val
- [x] Métriques accuracy + f1
- [x] Sérialisation du modèle (`save_model`, joblib)
- [ ] Seed déterministe + versioning des données (DVC ou hash dataset)
- [ ] Validation de schéma des données d'entrée (pandera)

## Tracking
- [x] `ExperimentTracker` (Protocol) + adaptateurs MLflow / NoOp
- [ ] Logguer aussi les hyperparamètres et tags de version
- [ ] Démarrer/fermer explicitement un run MLflow (context manager)

## Registry (JFrog)
- [x] `ArtifactRegistry.push()` / `pull()` vers Artifactory
- [ ] Promotion par tags (staging → production)
- [ ] Récupération du modèle au démarrage du service de serving

## Évaluation
- [x] Gate d'évaluation : `passes_gate` / `enforce_gate` sur seuil d'accuracy
- [ ] Comparaison vs baseline historique (pas seulement un seuil fixe)

## Orchestration
- [x] `runner.run_pipeline` train → log → save → push → gate
- [x] Entrée CLI `python -m pipeline`
- [ ] DAG Vertex AI Pipelines réel (composants train → eval → register)

## CI/CD
- [x] Jobs lint / typecheck / test (GitHub Actions)
- [ ] Job `train` (tag) + push artefact JFrog avec secrets masqués / Vault
- [ ] Job `deploy` (kubectl) staging/prod

## Tests
- [x] train (métriques, apprentissage, sérialisation), dataset, évaluation, registry, runner
- [ ] Tests d'intégration MLflow + JFrog (testcontainers)
