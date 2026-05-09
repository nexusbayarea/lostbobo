"""
OpenTelemetry Tracing + Jaeger Integration
"""

import os
from typing import Any

try:
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.trace import get_tracer

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False


def setup_tracing(service_name: str = "simhpc") -> Any:
    """Initialize OpenTelemetry with Jaeger exporter."""
    if not OTEL_AVAILABLE:
        return _NoOpTracer()

    resource = Resource(attributes={SERVICE_NAME: service_name})

    jaeger_host = os.getenv("JAEGER_AGENT_HOST", "localhost")
    jaeger_port = int(os.getenv("JAEGER_AGENT_PORT", "6831"))

    try:
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host,
            agent_port=jaeger_port,
        )
        trace.set_tracer_provider(TracerProvider(resource=resource))
        trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))
    except Exception:
        pass

    return get_tracer(__name__)


class _NoOpTracer:
    """Fallback when opentelemetry is not installed."""

    def start_as_current_span(self, name: str, attributes=None):
        return _NoOpSpan()


class _NoOpSpan:
    """Fallback span."""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


tracer = setup_tracing("simhpc")
