import asyncio
import os

import structlog
from opentelemetry import _logs, metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import BatchSpanProcessor, TracerProvider
from opentelemetry.semconv.resource import ResourceAttributes

from backend.core.kernel.kernel import Kernel
from backend.core.supabase_job_store import SupabaseJobStore

log = structlog.get_logger(__name__)


class ObservabilityService:
    """Complete OpenTelemetry: Traces + Metrics + Logs (Kernel-centered)"""

    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.supabase = SupabaseJobStore()

        resource = Resource.create(
            {
                ResourceAttributes.SERVICE_NAME: "simhpc",
                ResourceAttributes.SERVICE_VERSION: "0.4.0",
                ResourceAttributes.DEPLOYMENT_ENVIRONMENT: os.getenv("ENV", "production"),
            }
        )

        # === Tracing (Jaeger) ===
        trace.set_tracer_provider(TracerProvider(resource=resource))
        trace_exporter = OTLPSpanExporter(endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4317"))
        trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(trace_exporter))

        # === Metrics ===
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4317"))
        )
        meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        metrics.set_meter_provider(meter_provider)

        # === Logs ===
        logger_provider = LoggerProvider(resource=resource)
        _logs.set_logger_provider(logger_provider)
        log_exporter = OTLPLogExporter(endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4317"))
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

        self.logger = _logs.get_logger(__name__)
        self.tracer = trace.get_tracer(__name__)
        self.meter = metrics.get_meter(__name__)

        # Key OTEL Metrics
        self.request_counter = self.meter.create_counter("simhpc.requests", "Total HTTP requests", "1")
        self.request_duration_histogram = self.meter.create_histogram(
            "simhpc.request.duration", "Request duration", "s"
        )
        self.trust_score_gauge = self.meter.create_gauge("simhpc.trust.score", "Trust verification score")
        self.genai_fallback_counter = self.meter.create_counter("simhpc.genai.fallbacks", "GenAI fallback events")

    def start_span(self, name: str, attributes: dict = None):
        return self.tracer.start_span(name, attributes=attributes or {})

    def emit_log(self, level: str, message: str, attributes: dict = None):
        """Emit structured log via OTEL + correlate with Supabase"""
        attributes = attributes or {}
        # In a real impl, we'd pull the job ID from the current context

        # OTLP logging uses specific severity levels (standardized)
        self.logger.emit(
            body=message,
            severity_text=level,
            attributes={**attributes, "service.name": "simhpc", "simhpc.kernel": "true"},
        )

        # Also persist important logs to Supabase
        if level in ["ERROR", "CRITICAL"] or "trust" in message.lower():
            asyncio.create_task(
                self.supabase.record_event("otel_log", {"level": level, "message": message, "attributes": attributes})
            )

    async def record_observability_event(self, payload: dict):
        """Handler for RECORD_OBSERVABILITY command"""
        if payload.get("type") == "request":
            attributes = {
                "method": payload["method"],
                "route": payload["route"],
                "status": str(payload["status"]),
                "tenant_id": payload["tenant_id"],
            }
            self.request_counter.add(1, attributes)
            self.request_duration_histogram.record(payload["duration"], attributes)

            if payload["status"] >= 400 or payload["duration"] > 5.0:
                await self.supabase.record_event("high_latency_or_error", payload)
