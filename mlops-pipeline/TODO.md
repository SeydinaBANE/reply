# TODO — mlops-pipeline

## Entraînement
- [ ] Implémenter `train_model()` réel (sklearn/xgboost) avec split train/val
- [ ] Logguer params, métriques et artefact via MLflow
- [ ] Seed déterministe + versioning des données (DVC ou hash dataset)
- [ ] Validation de schéma des données d'entrée (pandera)

## Registry (JFrog)
- [ ] Implémenter `ArtifactRegistry.push()` / `pull()` vers Artifactory
- [ ] Promotion par tags (staging → production)
- [ ] Récupération du modèle au démarrage du service de serving

## Orchestration Vertex
- [ ] Compléter le DAG `vertex/pipeline.py` (composants train → eval → register)
- [ ] Gate d'évaluation : ne déployer que si métrique > seuil
- [ ] Planification (Vertex Pipelines Scheduler)

## CI/CD GitLab
- [ ] Job `train` déclenché sur tag, push artefact JFrog
- [ ] Job `build` + push image vers le registry GitLab
- [ ] Job `deploy` (kubectl) avec environnements staging/prod
- [ ] Secrets via variables CI masquées / Vault

## Tests
- [ ] `test_train_model_returns_metrics`
- [ ] `test_registry_push_invalid_path_raises`
