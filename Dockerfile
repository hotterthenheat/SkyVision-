FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md alembic.ini ./
COPY migrations ./migrations
COPY scripts ./scripts
COPY skyvision ./skyvision

RUN pip install --upgrade pip \
    && pip install .

EXPOSE 8000
CMD ["sh", "-c", "uvicorn skyvision.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
