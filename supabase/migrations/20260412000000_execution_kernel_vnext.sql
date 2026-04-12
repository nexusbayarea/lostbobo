-- Add tier and priority to users (if not already there, though we use it in jobs)
-- For now, let's assume we want to track it on simulations too for easier querying.
ALTER TABLE simulations ADD COLUMN IF NOT EXISTS tier text DEFAULT 'free';
ALTER TABLE simulations ADD COLUMN IF NOT EXISTS priority integer DEFAULT 0;
ALTER TABLE simulations ADD COLUMN IF NOT EXISTS fingerprint text;

-- Workflow Engine Schema
CREATE TABLE IF NOT EXISTS workflows (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id),
    name text NOT NULL,
    status text DEFAULT 'active', -- active, completed, failed, cancelled
    current_step integer DEFAULT 1,
    total_steps integer NOT NULL,
    state jsonb DEFAULT '{}',
    context jsonb DEFAULT '{}',
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- Workflow Steps (optional, but good for tracking)
CREATE TABLE IF NOT EXISTS workflow_steps (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id uuid REFERENCES workflows(id) ON DELETE CASCADE,
    step_number integer NOT NULL,
    name text NOT NULL,
    status text DEFAULT 'pending', -- pending, running, completed, failed
    job_id uuid, -- optional link to a job
    result jsonb,
    error text,
    started_at timestamp with time zone,
    completed_at timestamp with time zone
);
