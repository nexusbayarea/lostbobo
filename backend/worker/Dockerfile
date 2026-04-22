FROM python:3.11-slim

WORKDIR /app

COPY backend /app/backend

WORKDIR /app/backend

RUN python tools/env_bootstrap.py prod

COPY backend/worker/supervisor/simhpc.conf /etc/supervisor/conf.d/simhpc.conf

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/simhpc.conf"]