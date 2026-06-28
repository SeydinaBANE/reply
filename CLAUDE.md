# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A portfolio monorepo of **5 independent projects** built to match an AI Engineer / MLOps job
offer (see `offre.md`). Each top-level directory is a standalone project with its own
`pyproject.toml`, `Dockerfile`, infrastructure manifests, `README.md` and `TODO.md`.

| Directory | Purpose |
|-----------|---------|
| `rag-kubernetes/` | Enterprise RAG API (FastAPI) backed by pgvector + Redis, served on Kubernetes |
| `mlops-pipeline/` | Train → registry → deploy pipeline driven by GitLab CI and Vertex AI |
| `ml-observability/` | Model monitoring stack (Prometheus + Grafana) with data-drift detection |
| `llm-secure-inference/` | Secret-managed LLM inference API using Vault + K8s RBAC |
| `llm-finetuning/` | LoRA/QLoRA fine-tuning + automated evaluation harness on Vertex AI |

The projects are intentionally decoupled — there is **no shared package**. Work inside one
project directory at a time.

## Per-project commands

Each project uses the same tooling so the commands are uniform. Run them from inside a
project directory (e.g. `cd rag-kubernetes`):

```bash
make install      # create .venv and install deps + dev tools
make lint         # ruff check
make typecheck    # mypy src
make test         # pytest
make test-one T=tests/test_retrieval.py::test_retrieve_empty_corpus   # single test
make docker       # build the project image
```

If `make` is unavailable, the underlying commands are listed in each project's `Makefile`.

## Conventions (enforced)

- Strict typing on every function parameter and return value; no bare `Any`/`dict`/`list`.
- No comments in code — names must carry the intent.
- Config comes from env via `pydantic-settings` (`src/<pkg>/config.py`), never hardcoded.
- Business errors raised in the domain layer, caught at the API/presentation boundary.
- Tests named `test_<function>_<case>`; mock all external services (DB, Redis, LLM, GCP).

## Status

All projects are **scaffolds**. The concrete implementation work is tracked in each
project's `TODO.md`. Start there before writing code.
