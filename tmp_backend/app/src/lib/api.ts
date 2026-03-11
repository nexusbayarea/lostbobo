

// Point to the RunPod Proxy URL
const API_BASE_URL = 'https://8qvtqsc4zl5tms-8000.proxy.runpod.net/api/v1';
const API_KEY = 'shpc_live_8qvtqsc4zl5tms';

const headers = {
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY,
};

export interface ParameterConfig {
  name: string;
  base_value: number;
  unit: string;
  description: string;
  perturbable: boolean;
  min_value?: number;
  max_value?: number;
}

export interface RobustnessConfig {
  enabled: boolean;
  num_runs: number;
  sampling_method: string;
  parameters: ParameterConfig[];
  convergence_timeout_sec: number;
  random_seed?: number;
}

export interface RunStatusResponse {
  run_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: {
    current: number;
    total: number;
  };
  created_at: string;
  completed_at?: string;
  results?: any;
  ai_report?: any;
  config_summary?: any;
}

export const api = {
  async startRobustnessRun(config: any): Promise<RunStatusResponse> {
    const response = await fetch(`${API_BASE_URL}/robustness/run`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        config: {
          enabled: true,
          num_runs: config.numRuns,
          sampling_method: config.samplingMethod,
          parameters: config.parameters.map((p: any) => ({
            name: p.name,
            base_value: p.baseValue,
            unit: p.unit || '',
            description: p.description || '',
            perturbable: p.perturbable,
            min_value: p.min,
            max_value: p.max
          })),
          convergence_timeout_sec: config.timeout || 300,
          random_seed: config.seed
        }
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to start robustness run');
    }

    return response.json();
  },

  async getRunStatus(runId: string): Promise<RunStatusResponse> {
    const response = await fetch(`${API_BASE_URL}/robustness/status/${runId}`, { headers });
    if (!response.ok) {
      throw new Error('Failed to fetch run status');
    }
    return response.json();
  },

  async listRuns(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/robustness/runs`, { headers });
    if (!response.ok) {
      throw new Error('Failed to list runs');
    }
    return response.json();
  },

  async getSamplingMethods(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/sampling-methods`, { headers });
    if (!response.ok) {
      throw new Error('Failed to fetch sampling methods');
    }
    return response.json();
  },

  async cancelRobustnessRun(runId: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/robustness/cancel/${runId}`, {
      method: 'POST',
      headers,
    });
    if (!response.ok) {
      throw new Error('Failed to cancel robustness run');
    }
    return response.json();
  },

  async exportPdf(runId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/robustness/report/${runId}/pdf`, { headers });
    if (!response.ok) {
      throw new Error('Failed to export PDF');
    }
    return response.blob();
  }
};
