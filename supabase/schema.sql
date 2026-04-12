create table jobs (
  id uuid primary key default gen_random_uuid(),
  payload jsonb,
  status text, -- queued | leased | running | done | failed
  priority int default 0,
  fingerprint text,
  lease_id text,
  lease_expires_at timestamp,
  attempt_count int default 0,
  created_at timestamp default now()
);

create table users (
  id uuid primary key,
  tier text default 'free'
);