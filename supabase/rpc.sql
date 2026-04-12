-- Function to claim a job (lease-based)
create or replace function claim_job(
    p_worker_id text,
    p_lease_id text,
    p_lease_duration int default 300
) returns table (
    id uuid,
    payload jsonb,
    status text,
    priority int,
    fingerprint text,
    attempt_count int,
    created_at timestamp
) language sql as $$
    UPDATE jobs
    SET 
        status = 'leased',
        lease_id = p_lease_id,
        lease_expires_at = now() + (p_lease_duration || ' seconds')::interval
    WHERE id = (
        SELECT id FROM jobs
        WHERE status = 'queued'
        ORDER BY priority DESC, created_at ASC
        LIMIT 1
        FOR UPDATE SKIP LOCKED
    )
    RETURNING id, payload, status, priority, fingerprint, attempt_count, created_at;
$$;

-- Function to renew lease on a job
create or replace function renew_lease(
    p_job_id uuid,
    p_lease_id text,
    p_lease_duration int default 300
) returns boolean language sql as $$
    UPDATE jobs
    SET 
        lease_expires_at = now() + (p_lease_duration || ' seconds')::interval
    WHERE id = p_job_id
      AND lease_id = p_lease_id
      AND lease_expires_at > now()
    RETURNING true;
$$;