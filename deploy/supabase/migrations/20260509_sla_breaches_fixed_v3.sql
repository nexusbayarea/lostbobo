-- 1. SLA Breaches Table
CREATE TABLE IF NOT EXISTS sla_breaches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    breach_id TEXT UNIQUE NOT NULL,
    sla_tier TEXT NOT NULL,
    breach_type TEXT NOT NULL,
    description TEXT,
    run_id TEXT,
    tenant_id TEXT,
    affected_node_id TEXT,
    started_at TIMESTAMPTZ NOT NULL,
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    credit_usd NUMERIC(10,4) DEFAULT 0,
    severity TEXT DEFAULT 'MEDIUM',
    root_cause TEXT,
    resolution_minutes DOUBLE PRECISION,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_sla_breaches_tier ON sla_breaches(sla_tier, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sla_breaches_type ON sla_breaches(breach_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sla_breaches_root ON sla_breaches(root_cause);
CREATE INDEX IF NOT EXISTS idx_sla_breaches_run ON sla_breaches(run_id);
CREATE INDEX IF NOT EXISTS idx_sla_breaches_tenant ON sla_breaches(tenant_id, created_at DESC);

-- 2. SLA Events Table
CREATE TABLE IF NOT EXISTS sla_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    breach_id UUID REFERENCES sla_breaches(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sla_events_breach ON sla_events(breach_id);

-- 3. RLS Policies
ALTER TABLE sla_breaches ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_full_access" ON sla_breaches;
CREATE POLICY "service_role_full_access"
    ON sla_breaches
    TO service_role
    USING (true)
    WITH CHECK (true);

ALTER TABLE sla_events ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_full_access" ON sla_events;
CREATE POLICY "service_role_full_access"
    ON sla_events
    TO service_role
    USING (true)
    WITH CHECK (true);

-- 4. Materialized View + Required Unique Index
DROP MATERIALIZED VIEW IF EXISTS sla_breach_summary;

CREATE MATERIALIZED VIEW sla_breach_summary AS
SELECT
    sla_tier,
    COUNT(*) as breach_count,
    SUM(credit_usd) as total_credits_usd,
    AVG(resolution_minutes) as avg_resolution_min,
    MAX(created_at) as last_breach
FROM sla_breaches
GROUP BY sla_tier;

CREATE UNIQUE INDEX IF NOT EXISTS idx_sla_breach_summary_tier
    ON sla_breach_summary(sla_tier);

REFRESH MATERIALIZED VIEW sla_breach_summary;
