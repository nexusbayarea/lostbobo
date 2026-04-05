-- 005_engineer_notebook.sql
-- Engineer Notebook table for per-user simulation notes

CREATE TABLE IF NOT EXISTS notebooks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  context TEXT,
  parameters TEXT,
  observations TEXT,
  hypotheses TEXT,
  next_experiments TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT notebooks_user_id_unique UNIQUE (user_id)
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_notebooks_user_id ON notebooks(user_id);

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_notebook_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_notebook_updated_at ON notebooks;
CREATE TRIGGER set_notebook_updated_at
  BEFORE UPDATE ON notebooks
  FOR EACH ROW
  EXECUTE FUNCTION update_notebook_updated_at();

-- RLS
ALTER TABLE notebooks ENABLE ROW LEVEL SECURITY;

-- Users can only see and manage their own notebook
CREATE POLICY "Users can manage their own notebook"
  ON notebooks
  FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
