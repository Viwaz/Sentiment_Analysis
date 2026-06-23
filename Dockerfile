"""
Dockerfile
Build image for the FastAPI backend (model_api, auth, DB helpers).
"""
FROM python:3.11-slim

# Install OS deps (psycopg2 needs libpq-dev and gcc)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirement files first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src ./src
COPY Database ./Database

EXPOSE 8000

CMD ["uvicorn", "src.model_api:app", "--host", "0.0.0.0", "--port", "8000"]
