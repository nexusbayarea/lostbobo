CREATE TABLE IF NOT EXISTS strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    contract_hash TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS strategy_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id UUID REFERENCES strategies(id),
    run_id UUID REFERENCES walk_forward_runs(id),
    metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orchestrator_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_run_id UUID REFERENCES walk_forward_runs(id),
    allocation JSONB,
    final_metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
