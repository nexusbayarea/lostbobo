export interface Parameter {
  name: string;
  baseValue: number;
  unit: string;
  perturbable: boolean;
  min: number;
  max: number;
}

interface ConfigurationPanelProps {
  enabled: boolean;
  onEnabledChange: (enabled: boolean) => void;
  numRuns: number;
  onNumRunsChange: (n: number) => void;
  samplingMethod: string;
  onSamplingMethodChange: (m: string) => void;
  parameters: Parameter[];
  onParametersChange: (p: Parameter[]) => void;
  timeout: number;
  onTimeoutChange: (t: number) => void;
  seed?: number;
  onSeedChange: (s?: number) => void;
}

const samplingMethods = ['±10% Range (Random)', '±5% Range (Random)', '±20% Range (Random)', 'Latin Hypercube'];

export function ConfigurationPanel({
  numRuns, onNumRunsChange, samplingMethod, onSamplingMethodChange,
  parameters, onParametersChange, timeout, onTimeoutChange, seed, onSeedChange,
}: ConfigurationPanelProps) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
      <h2 className="text-xl font-bold text-white">Configuration</h2>

      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Number of Runs</label>
          <input
            type="number"
            value={numRuns}
            onChange={(e) => onNumRunsChange(parseInt(e.target.value) || 1)}
            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white"
            min={1}
            max={1000}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Sampling Method</label>
          <select
            value={samplingMethod}
            onChange={(e) => onSamplingMethodChange(e.target.value)}
            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white"
          >
            {samplingMethods.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Timeout (seconds)</label>
          <input
            type="number"
            value={timeout}
            onChange={(e) => onTimeoutChange(parseInt(e.target.value) || 300)}
            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white"
            min={60}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Seed (optional)</label>
          <input
            type="number"
            value={seed ?? ''}
            onChange={(e) => onSeedChange(e.target.value ? parseInt(e.target.value) : undefined)}
            className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white"
            placeholder="Random"
          />
        </div>
      </div>

      <div>
        <h3 className="text-sm font-medium text-slate-300 mb-3">Parameters</h3>
        <div className="space-y-3">
          {parameters.map((param, i) => (
            <div key={i} className="flex items-center gap-4 bg-slate-800 rounded-xl px-4 py-3">
              <div className="flex-1">
                <span className="text-white text-sm font-medium">{param.name}</span>
                <span className="text-slate-400 text-xs ml-2">{param.unit}</span>
              </div>
              <span className="text-cyan-400 text-sm font-mono">{param.baseValue}</span>
              <span className={`text-xs px-2 py-1 rounded-full ${param.perturbable ? 'bg-cyan-500/10 text-cyan-400' : 'bg-slate-700 text-slate-400'}`}>
                {param.perturbable ? 'Perturbable' : 'Fixed'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
