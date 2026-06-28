FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install .

COPY src ./src
RUN pip install --no-deps -e .

EXPOSE 8000
USER 1000
CMD ["uvicorn", "inference.main:app", "--host", "0.0.0.0", "--port", "8000"]
