# AI Engineer — Portfolio (5 projets)

[![CI](https://github.com/SeydinaBANE/reply/actions/workflows/ci.yml/badge.svg)](https://github.com/SeydinaBANE/reply/actions/workflows/ci.yml)

Monorepo de 5 projets  : conception,
industrialisation et déploiement de solutions IA en production (MLOps / GenAI).

| # | Projet | Dossier | Compétences clés démontrées |
|---|--------|---------|------------------------------|
| 1 | RAG d'entreprise sur Kubernetes | [`rag-kubernetes/`](rag-kubernetes/) | RAG, vector DB (pgvector), Redis, Vertex AI, Docker, K8s |
| 2 | Pipeline MLOps train → registry → deploy | [`mlops-pipeline/`](mlops-pipeline/) | GitLab CI/CD, JFrog, MLflow, Vertex AI Pipelines, K8s |
| 3 | Observabilité des modèles en production | [`ml-observability/`](ml-observability/) | Grafana, Prometheus, Redis, PostgreSQL, drift detection |
| 4 | Service d'inférence LLM sécurisé | [`llm-secure-inference/`](llm-secure-inference/) | Vault, K8s RBAC, Redis rate-limiting, FastAPI |
| 5 | Fine-tuning + évaluation d'un LLM | [`llm-finetuning/`](llm-finetuning/) | Vertex AI training, LoRA/QLoRA, eval harness, CI |

## Couverture du stack de l'offre

Python · Git/GitLab · Docker · Kubernetes · Vault · JFrog · Grafana · Redis ·
PostgreSQL · GCP Vertex AI · RAG / vector databases · fine-tuning

## Démarrage

Chaque projet est autonome. Voir le `README.md` et le `TODO.md` de chaque dossier.

```bash
cd rag-kubernetes && cat TODO.md
```
