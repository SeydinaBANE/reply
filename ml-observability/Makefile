.PHONY: install lint typecheck test test-one docker
IMAGE ?= ml-observability:0.1.0

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

docker:
	docker build -t $(IMAGE) .
