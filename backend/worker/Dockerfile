FROM python:3.11-slim

WORKDIR /app

RUN pip install uv supervisor requests

COPY pyproject.toml uv.lock ./
COPY app ./app
COPY packages ./packages
COPY worker ./worker

RUN uv pip install --system -e .

COPY worker/supervisor/simhpc.conf /etc/supervisor/conf.d/simhpc.conf

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/simhpc.conf"]
