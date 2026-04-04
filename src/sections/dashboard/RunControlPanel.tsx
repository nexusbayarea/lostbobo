import { Play, Square, Zap, BarChart3 } from 'lucide-react';

interface RunControlPanelProps {
  onStartRun: () => void;
  onCancelRun: () => void;
  isRunning: boolean;
  numRuns: number;
  samplingMethod: string;
  activeParams: number;
  userBalance: number;
}

export function RunControlPanel({
  onStartRun, onCancelRun, isRunning, numRuns, samplingMethod, activeParams, userBalance,
}: RunControlPanelProps) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${isRunning ? 'bg-cyan-400 animate-pulse' : 'bg-slate-600'}`} />
          <h2 className="text-xl font-bold text-white">Run Control</h2>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <Zap className="w-4 h-4 text-yellow-400" />
          Balance: ${userBalance}
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-800 rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-white">{numRuns}</div>
          <div className="text-xs text-slate-400 mt-1">Runs</div>
        </div>
        <div className="bg-slate-800 rounded-xl p-4 text-center">
          <div className="text-2xl font-bold text-white">{activeParams}</div>
          <div className="text-xs text-slate-400 mt-1">Params</div>
        </div>
        <div className="bg-slate-800 rounded-xl p-4 text-center">
          <BarChart3 className="w-6 h-6 text-cyan-400 mx-auto mb-1" />
          <div className="text-xs text-slate-400">{samplingMethod.split('(')[0].trim()}</div>
        </div>
        <div className="bg-slate-800 rounded-xl p-4 text-center">
          <div className={`text-sm font-bold ${isRunning ? 'text-cyan-400' : 'text-slate-400'}`}>
            {isRunning ? 'Running' : 'Idle'}
          </div>
          <div className="text-xs text-slate-400 mt-1">Status</div>
        </div>
      </div>

      <div className="flex gap-3">
        <button
          onClick={onStartRun}
          disabled={isRunning}
          className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-cyan-500 hover:bg-cyan-600 text-white font-medium rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Play className="w-4 h-4" /> Run Simulation
        </button>
        <button
          onClick={onCancelRun}
          disabled={!isRunning}
          className="flex items-center justify-center gap-2 px-6 py-3 bg-red-500/10 hover:bg-red-500/20 text-red-400 font-medium rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed border border-red-500/20"
        >
          <Square className="w-4 h-4" /> Cancel
        </button>
      </div>
    </div>
  );
}
