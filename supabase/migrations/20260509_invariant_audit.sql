-- Invariant Registry Audit Table
-- Records all invariant violations for compliance auditing

CREATE TABLE IF NOT EXISTS invariant_violations (
    violation_id    TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    event_id        TEXT NOT NULL,
    violations      JSONB NOT NULL DEFAULT '[]',
    state_id       TEXT,
    event_type     TEXT,
    source_plugin   TEXT,
    resolved        BOOLEAN NOT NULL DEFAULT false,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_invariant_violations_event ON invariant_violations (event_id);
CREATE INDEX IF NOT EXISTS idx_invariant_violations_resolved ON invariant_violations (resolved);
CREATE INDEX IF NOT EXISTS idx_invariant_violations_created ON invariant_violations (created_at DESC);

ALTER TABLE invariant_violations ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "invariant_violations_read" ON invariant_violations FOR SELECT USING (true);
CREATE POLICY IF NOT EXISTS "invariant_violations_insert" ON invariant_violations FOR INSERT WITH CHECK (true);

GRANT SELECT, INSERT ON invariant_violations TO anon, authenticated, service_role;
