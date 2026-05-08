import os

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes

from backend.core.kernel.kernel import Kernel
from backend.core.supabase_job_store import SupabaseJobStore


class ObservabilityService:
    """Unified OpenTelemetry Traces + Metrics (Kernel-centered)"""

    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.supabase = SupabaseJobStore()

        resource = Resource.create(
            {
                ResourceAttributes.SERVICE_NAME: "simhpc",
                ResourceAttributes.SERVICE_VERSION: "0.4.0",
            }
        )

        # === Tracing (Jaeger via OTLP) ===
        trace.set_tracer_provider(TracerProvider(resource=resource))
        trace_exporter = OTLPSpanExporter(endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4317"))
        trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(trace_exporter))

        # === Metrics (OTEL + Prometheus Bridge) ===
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4317"))
        )
        meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        metrics.set_meter_provider(meter_provider)

        self.meter = metrics.get_meter(__name__)
        self.tracer = trace.get_tracer(__name__)

        # Key OTEL Metrics
        self.request_counter = self.meter.create_counter("simhpc.requests", "Total HTTP requests", "1")
        self.request_duration_histogram = self.meter.create_histogram(
            "simhpc.request.duration", "Request duration", "s"
        )
        self.trust_score_gauge = self.meter.create_gauge("simhpc.trust.score", "Trust verification score")
        self.genai_fallback_counter = self.meter.create_counter("simhpc.genai.fallbacks", "GenAI fallback events")

    async def record_observability_event(self, payload: dict):
        """Handler for RECORD_OBSERVABILITY command"""
        if payload.get("type") == "request":
            await self.record_request(
                payload["method"], payload["route"], payload["status"], payload["duration"], payload["tenant_id"]
            )

    async def record_request(self, method: str, route: str, status: int, duration: float, tenant_id: str = "unknown"):
        attributes = {"method": method, "route": route, "status": str(status), "tenant_id": tenant_id}

        self.request_counter.add(1, attributes)
        self.request_duration_histogram.record(duration, attributes)

        # Persist key metrics to Supabase for long-term truth
        if status >= 400 or duration > 5.0:
            await self.supabase.record_event(
                "high_latency_or_error",
                {"route": route, "status": status, "duration": duration, "tenant_id": tenant_id},
            )
