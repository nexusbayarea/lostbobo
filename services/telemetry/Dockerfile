FROM grafana/grafana:latest AS grafana
FROM prom/prometheus:latest AS prometheus
FROM otel/opentelemetry-collector-contrib:latest AS otel

FROM alpine:latest

RUN apk add --no-cache bash

COPY --from=prometheus /bin/prometheus /usr/local/bin/prometheus
COPY --from=prometheus /etc/prometheus/prometheus.yml /etc/prometheus/prometheus.yml

COPY --from=grafana /usr/share/grafana /usr/share/grafana
COPY --from=grafana /usr/sbin/grafana-server /usr/sbin/grafana-server
COPY --from=grafana /usr/sbin/grafana-cli /usr/sbin/grafana-cli

COPY --from=otel /otelcol-contrib /usr/local/bin/otelcol-contrib

COPY prometheus.yml /etc/prometheus/prometheus.yml

RUN mkdir -p /etc/otel && \
    echo 'receivers:\n  otlp:\n    protocols:\n      grpc:\n        endpoint: 0.0.0.0:4317\n      http:\n        endpoint: 0.0.0.0:4318\nexporters:\n  prometheus:\n    endpoint: 0.0.0.0:8889\nservice:\n  pipelines:\n    metrics:\n      receivers: [otlp]\n      exporters: [prometheus]' > /etc/otel/config.yml

COPY start-telemetry.sh /start-telemetry.sh
RUN chmod +x /start-telemetry.sh

EXPOSE 9090 3000 4317 4318

CMD ["/start-telemetry.sh"]
