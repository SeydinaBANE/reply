# AGENTS.md — reply monorepo

## Structure

5 independent Python projects, no shared package. Work inside one project directory.

| Directory | Package name (`src/<pkg>/`) | Entry point |
|-----------|-----------------------------|-------------|
| `rag-kubernetes/` | `rag_service` | FastAPI `rag_service.main:app` (`make run`) |
| `mlops-pipeline/` | `pipeline` | CLI `python -m pipeline` (no HTTP server) |
| `ml-observability/` | `monitor` | FastAPI `monitor.main:app` (no `make run`) |
| `llm-secure-inference/` | `inference` | FastAPI `inference.main:app` (`make run`) |
| `llm-finetuning/` | `finetune` | CLI `python -m finetune` (no HTTP server) |

## Developer commands

Run from inside a project directory. All targets use `.venv/bin/` wrapper.

```bash
make install      # .venv + pip install -e ".[dev]"
make lint         # ruff check src tests
make typecheck    # mypy src          (source only, NOT tests)
make test         # pytest -q
make test-one T=tests/test_foo.py::test_bar
make run          # uvicorn — only rag-kubernetes, llm-secure-inference
make docker       # docker build -t <IMAGE> .
```

CI (`.github/workflows/ci.yml`) runs: `pip install -e ".[dev]"` → `ruff check src tests` → `mypy src` → `pytest -q`. Python 3.11, GitHub Actions matrix across all 5 projects. **No GitLab pipeline exists.**

## Conventions

- Strict typing: every parameter and return value annotated. No bare `Any`/`dict`/`list`.
- No comments in code — names carry intent.
- Config via `pydantic-settings` from `.env` (`src/<pkg>/config.py`).
- Business errors raised in domain layer, caught at API boundary.
- Tests named `test_<function>_<case>`.
- **All external services mocked** via `Fake*` classes (FakeRedis, FakeStore, FakeEmbedder, etc.) — no real DB/Redis/LLM in tests.
- API tests use `app.dependency_overrides` pattern + `TestClient` (see `rag-kubernetes/tests/test_api.py`).
- Async test projects use `asyncio_mode = "auto"` in pyproject.toml + `@pytest.mark.asyncio`.

## Build & tooling

- `ruff`: line-length=100, target-version=py311
- `mypy`: strict, pydantic plugin, `ignore_missing_imports` for GCP/ML libraries
- `pytest`: `pythonpath = ["src"]` in 3/5 projects (rag-kubernetes, ml-observability, llm-finetuning); the other two rely on editable install
- Build backend: setuptools (not poetry/uv/pdm). Python >=3.11.
- Docker: `python:3.11-slim`, install non-editable then `pip install --no-deps -e .`

## Prerequisites per project

- **rag-kubernetes**: needs `psql "$DATABASE_URL" -f migrations/001_init.sql` before running
- **llm-secure-inference**: needs Vault running with secrets at configured path
- **ml-observability**: needs PostgreSQL + Redis; exposes `/metrics` at Prometheus endpoint
- CLI projects: `mlops-pipeline --data <path>` (CSV dataset), `llm-finetuning --eval-data <path>` (JSONL eval samples)

## K8s

Only `rag-kubernetes/k8s/` and `llm-secure-inference/k8s/` have manifests.

## Remaining work

Each project has a `TODO.md` listing unimplemented features. Read it before extending a project.
