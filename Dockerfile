FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-dev.txt /app/
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

COPY . /app

RUN pip install --no-deps -e .

CMD ["pytest", "--cov=src", "--cov-report=term-missing"]
