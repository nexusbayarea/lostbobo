export interface SimulationUpdate {
  id: string;
  status: string;
  scenario_name: string | null;
  job_id: string | null;
}

export interface SimulationInsert {
  id: string;
  user_id: string;
  status: string;
  created_at: string;
}
