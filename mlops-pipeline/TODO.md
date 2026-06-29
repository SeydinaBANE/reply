# TODO — mlops-pipeline

## Entraînement
- [x] Implémenter `train_model()` (LogisticRegression + StandardScaler) avec split train/val
- [x] Métriques accuracy + f1 (binaire/macro selon le nombre de classes)
- [x] Sérialisation du modèle (`save_model`, joblib)
- [x] `train_test_split` stratifié
- [x] Seed déterministe + hash du dataset
- [x] Validation de schéma des données d'entrée (pandera + équilibre des classes)

## Tracking
- [x] `ExperimentTracker` (Protocol) + adaptateurs MLflow / NoOp
- [x] Logguer hyperparamètres + tags de version (hash dataset)
- [x] Run MLflow géré explicitement (context manager)
- [x] `mlflow.sklearn.log_model` avec signature inférée

## Registry (JFrog)
- [x] `ArtifactRegistry.push()` / `pull()` vers Artifactory
- [x] Streaming + retry/backoff + timeouts configurables
- [ ] Promotion par tags (staging → production)
- [ ] Récupération du modèle au démarrage du service de serving

## Évaluation
- [x] Gate d'évaluation : `passes_gate` / `enforce_gate` sur seuil d'accuracy
- [x] Gate exécuté AVANT toute publication (un modèle recalé n'est pas poussé)
- [x] Comparaison vs baseline historique (avec tolérance)

## Orchestration
- [x] `runner.run_pipeline` train → log → gate → save → log_model → push
- [x] Entrée CLI `python -m pipeline`
- [x] Spec DAG Vertex (composants + dépendances validées)
- [ ] DAG Vertex AI Pipelines réel via KFP (compilation + soumission)

## CI/CD GitLab
- [x] Jobs lint / typecheck / test
- [x] Job `train` (tag) sur `data/sample.csv` + artefact
- [x] Job `deploy` (kubectl) staging avec gate de rollout + smoke test + rollback
- [x] Secrets masqués/Vault documentés
- [ ] Job `train` réel sur données versionnées (DVC) + push JFrog via Vault

## Tests
- [x] train (métriques, apprentissage, sérialisation, multiclasse), dataset, évaluation, registry, runner
- [x] Régression : le gate empêche la publication ; retry JFrog ; baseline ; validation/hash
- [ ] Tests d'intégration MLflow + JFrog (testcontainers)
