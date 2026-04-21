-- 1. Create feature_registry table
CREATE TABLE IF NOT EXISTS feature_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    description TEXT,
    source_type TEXT CHECK (source_type IN ('raw', 'derived')),
    computation TEXT NOT NULL,
    lookback_window INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(name, version)
);

-- 2. Create feature_values table
CREATE TABLE IF NOT EXISTS feature_values (
    id BIGSERIAL PRIMARY KEY,
    feature_id UUID REFERENCES feature_registry(id),
    asset_id TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    value DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create index for feature lookup
CREATE INDEX IF NOT EXISTS idx_feature_lookup
ON feature_values (feature_id, asset_id, timestamp DESC);

-- 4. Create feature_lineage table
CREATE TABLE IF NOT EXISTS feature_lineage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feature_id UUID REFERENCES feature_registry(id),
    depends_on JSONB,
    contract_hash TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
