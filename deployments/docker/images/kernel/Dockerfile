FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

COPY deployments/runtime/ ./deployments/runtime/

ARG IMAGE_HASH
ENV SIMHPC_IMAGE_HASH=${IMAGE_HASH:-dev}
ENV PYTHONUNBUFFERED=1
ENV SIMHPC_RUNTIME=kernel

ENTRYPOINT ["bash", "deployments/scripts/entrypoint_kernel.sh"]
