export interface RunStatusResponse {
  id: string;
  job_id: string;
  status: 'idle' | 'processing' | 'completed' | 'failed';
  progress: number;
  certificate_hash?: string;
  credit_cost: number;
  last_ping?: string;
  created_at: string;
}
