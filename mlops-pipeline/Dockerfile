# Pin by digest in production: python:3.11-slim@sha256:<digest>
FROM python:3.11.9-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install .

COPY src ./src
RUN pip install --no-deps -e .

USER 1000
ENTRYPOINT ["python", "-m", "pipeline"]
