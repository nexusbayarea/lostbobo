#!/bin/bash
set -e

echo "=== SimHPC Telemetry Starting ==="

echo "Starting Prometheus..."
nohup prometheus --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/prometheus \
    --web.console.libraries=/usr/share/prometheus/console_libraries \
    --web.console.templates=/usr/share/prometheus/consoles \
    > /var/log/prometheus.log 2>&1 &

echo "Starting Grafana..."
nohup grafana-server --homepath=/usr/share/grafana \
    > /var/log/grafana.log 2>&1 &

echo "Starting OTEL Collector..."
nohup otelcol-contrib --config=/etc/otel/config.yml \
    > /var/log/otel.log 2>&1 &

echo "=== Telemetry Stack Started ==="
echo "Prometheus:  http://0.0.0.0:9090"
echo "Grafana:     http://0.0.0.0:3000"
echo "OTEL gRPC:   0.0.0.0:4317"
echo "OTEL HTTP:   0.0.0.0:4318"

tail -f /var/log/prometheus.log /var/log/grafana.log /var/log/otel.log
