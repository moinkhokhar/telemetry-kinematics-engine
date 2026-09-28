FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi --no-root

COPY . .

RUN poetry install --no-interaction --no-ansi --no-deps


FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app/src /app/src
COPY --from=builder --chown=appuser:appuser /app/pyproject.toml /app/pyproject.toml

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 50051/udp 8080

CMD ["python", "-m", "src"]
