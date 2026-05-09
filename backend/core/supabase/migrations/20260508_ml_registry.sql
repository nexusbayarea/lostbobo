CREATE TABLE IF NOT EXISTS model_registry (
    model_id TEXT PRIMARY KEY,
    version TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    benchmark_data JSONB NOT NULL,
    overall_score DOUBLE PRECISION,
    trained_on_runs INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS inference_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    task_type TEXT,
    domain TEXT,
    model_used TEXT,
    latency_ms DOUBLE PRECISION,
    confidence DOUBLE PRECISION,
    fallback_used BOOLEAN DEFAULT FALSE,
    tenant_id TEXT
);

CREATE INDEX IF NOT EXISTS idx_model_registry_score ON model_registry(overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_inference_logs_time ON inference_logs(timestamp DESC);
