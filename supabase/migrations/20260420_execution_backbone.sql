CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES walk_forward_runs(id),
    window_id UUID REFERENCES walk_forward_windows(id),
    asset_id TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    side TEXT CHECK (side IN ('buy', 'sell')),
    quantity FLOAT NOT NULL,
    order_type TEXT CHECK (order_type IN ('market', 'limit')),
    limit_price FLOAT,
    status TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    price FLOAT NOT NULL,
    quantity FLOAT NOT NULL,
    slippage FLOAT DEFAULT 0,
    fee FLOAT DEFAULT 0
);
