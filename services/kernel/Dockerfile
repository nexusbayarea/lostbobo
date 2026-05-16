FROM python:3.11-slim AS base

LABEL org.simhpc.component="kernel"
LABEL org.simhpc.plane="control"
LABEL org.simhpc.version="${RUNTIME_VERSION}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY ../backend /app/backend
COPY ../deployment/config /app/deployment/config

RUN useradd --create-home --shell /bin/bash simhpc && \
    chown -R simhpc:simhpc /app
USER simhpc

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080 50054

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
