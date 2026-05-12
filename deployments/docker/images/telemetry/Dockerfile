FROM python:3.12-slim

WORKDIR /app

COPY requirements-telemetry.txt .
RUN pip install --no-cache-dir -r requirements-telemetry.txt

COPY backend/ ./backend/
COPY deployments/runtime/ ./deployments/runtime/

ENV PYTHONUNBUFFERED=1
ENV SIMHPC_RUNTIME=telemetry

CMD ["python3", "-m", "backend.runtime.telemetry"]
