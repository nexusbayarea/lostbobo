FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/worker-service/ ./
COPY backend ./backend/

CMD ["python", "-u", "worker.py"]
