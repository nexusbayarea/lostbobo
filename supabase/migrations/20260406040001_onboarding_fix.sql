-- Fix missing columns for frontend sync
ALTER TABLE public.onboarding_state
  DROP COLUMN IF EXISTS step,
  DROP COLUMN IF EXISTS data,
  DROP COLUMN IF EXISTS completed;

ALTER TABLE public.onboarding_state
  ADD COLUMN IF NOT EXISTS current_step text default 'welcome',
  ADD COLUMN IF NOT EXISTS completed_steps jsonb default '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS events jsonb default '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS skipped boolean default false,
  ADD COLUMN IF NOT EXISTS version integer default 1;

NOTIFY pgrst, 'reload schema';
