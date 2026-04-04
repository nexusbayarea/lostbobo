import { BarChart3, CheckCircle, Clock } from 'lucide-react';

interface ResultsPanelProps {
  run: {
    run_id: string;
    results: unknown;
    progress: number;
  };
}

export function ResultsPanel({ run }: ResultsPanelProps) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">Results</h2>
        <div className="flex items-center gap-2">
          {run.progress === 100 ? (
            <CheckCircle className="w-5 h-5 text-emerald-400" />
          ) : (
            <Clock className="w-5 h-5 text-yellow-400" />
          )}
          <span className="text-sm text-slate-400">{run.progress}%</span>
        </div>
      </div>

      <div className="bg-slate-800 rounded-xl p-4">
        <div className="flex items-center gap-3 mb-2">
          <BarChart3 className="w-5 h-5 text-cyan-400" />
          <span className="text-white font-medium">Run ID</span>
        </div>
        <code className="text-cyan-400 text-sm font-mono">{run.run_id}</code>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="bg-slate-800 rounded-xl p-4">
          <div className="text-sm text-slate-400 mb-1">Status</div>
          <div className="text-lg font-bold text-emerald-400">Completed</div>
        </div>
        <div className="bg-slate-800 rounded-xl p-4">
          <div className="text-sm text-slate-400 mb-1">Progress</div>
          <div className="text-lg font-bold text-white">{run.progress}%</div>
        </div>
        <div className="bg-slate-800 rounded-xl p-4">
          <div className="text-sm text-slate-400 mb-1">Method</div>
          <div className="text-lg font-bold text-white">Monte Carlo</div>
        </div>
      </div>
    </div>
  );
}
