# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A portfolio monorepo of **5 independent projects** built to match an AI Engineer / MLOps job
offer. Each top-level directory is a standalone project with its own
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
make run          # start the service (uvicorn) where the project exposes an API
make docker       # build the project image
```

If `make` is unavailable, the underlying commands are listed in each project's `Makefile`.
The Python package name under `src/` differs per project (e.g. `rag_service`,
`pipeline`, `monitor`, `inference`, `finetune`) — `mypy`/`ruff` target `src` and `tests`.

CI runs as a single GitHub Actions matrix (`.github/workflows/ci.yml`) that executes
`ruff check`, `mypy src`, and `pytest -q` for each project in its own working directory
(Python 3.11). There is no GitLab pipeline despite what some project READMEs describe.

## Conventions (enforced)

- Strict typing on every function parameter and return value; no bare `Any`/`dict`/`list`.
- No comments in code — names must carry the intent.
- Config comes from env via `pydantic-settings` (`src/<pkg>/config.py`), never hardcoded.
- Business errors raised in the domain layer, caught at the API/presentation boundary.
- Tests named `test_<function>_<case>`; mock all external services (DB, Redis, LLM, GCP).

## Status

The core of each project is **implemented** (domain logic, FastAPI/CLI entry points,
tests). Remaining work — optional features and hardening — is tracked as unchecked items
in each project's `TODO.md`. Read that file before extending a project so new work fits
the intended design.
