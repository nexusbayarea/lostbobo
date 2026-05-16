FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

LABEL org.simhpc.component="gpu-worker"
LABEL org.simhpc.plane="simulation"
LABEL org.simhpc.version="${RUNTIME_VERSION}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-dev \
    python3-pip \
    build-essential \
    cmake \
    git \
    libopenmpi-dev \
    openmpi-bin \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/gpu-worker/ ./
COPY backend ./backend/
COPY deployment/config ./deployment/config

RUN useradd --create-home --shell /bin/bash simhpc && \
    chown -R simhpc:simhpc /app
USER simhpc

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import grpc; ch = grpc.insecure_channel('localhost:50053'); grpc.channel_ready_future(ch).result(timeout=5)" || exit 1

EXPOSE 50053

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-u", "sim_server.py"]
