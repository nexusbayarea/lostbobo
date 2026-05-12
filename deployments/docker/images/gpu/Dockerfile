FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 python3.12-venv python3.12-dev python3-pip git \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

COPY requirements-gpu.txt .
RUN pip install --no-cache-dir -r requirements-gpu.txt

COPY backend/ ./backend/
COPY deployments/runtime/ ./deployments/runtime/

ARG IMAGE_HASH
ENV SIMHPC_IMAGE_HASH=${IMAGE_HASH:-dev}
ENV PYTHONUNBUFFERED=1
ENV SIMHPC_RUNTIME=gpu-worker

ENTRYPOINT ["bash", "deployments/scripts/entrypoint_gpu.sh"]
