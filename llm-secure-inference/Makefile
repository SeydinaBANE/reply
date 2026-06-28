.PHONY: install lint typecheck test test-one run docker
IMAGE ?= llm-secure-inference:0.1.0

install:
	python -m venv .venv && .venv/bin/pip install -e ".[dev]"

lint:
	.venv/bin/ruff check src tests

typecheck:
	.venv/bin/mypy src

test:
	.venv/bin/pytest -q

test-one:
	.venv/bin/pytest -q $(T)

run:
	.venv/bin/uvicorn inference.main:app --host 0.0.0.0 --port 8000

docker:
	docker build -t $(IMAGE) .
