FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/module-runtime/ ./
COPY plugins ./plugins/

EXPOSE 50052

CMD ["python", "-u", "main.py"]
