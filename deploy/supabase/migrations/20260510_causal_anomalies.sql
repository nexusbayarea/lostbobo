-- 20260510_causal_anomalies.sql
-- Causal anomaly detection storage for runtime primitives

CREATE TABLE IF NOT EXISTS runtime_causal_anomalies (
    anomaly_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    anomaly_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    description TEXT,
    affected_entities TEXT[],
    confidence REAL,
    causal_id TEXT,
    timestamp DOUBLE PRECISION DEFAULT EXTRACT(EPOCH FROM NOW()),
    evidence JSONB
);

CREATE INDEX idx_anomalies_ts ON runtime_causal_anomalies (timestamp DESC);
CREATE INDEX idx_anomalies_type ON runtime_causal_anomalies (anomaly_type);
CREATE INDEX idx_anomalies_severity ON runtime_causal_anomalies (severity);
CREATE INDEX idx_anomalies_causal_id ON runtime_causal_anomalies (causal_id);

ALTER TABLE runtime_causal_anomalies ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role can manage anomalies"
    ON runtime_causal_anomalies
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Authenticated users can read anomalies"
    ON runtime_causal_anomalies
    FOR SELECT
    TO authenticated
    USING (true);