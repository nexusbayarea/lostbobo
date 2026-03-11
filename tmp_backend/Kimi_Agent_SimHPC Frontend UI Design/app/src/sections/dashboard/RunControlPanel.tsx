import { motion } from 'framer-motion';
import { Play, Loader2, CheckCircle2, Clock, Cpu, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';

interface RunControlPanelProps {
  onStartRun: () => void;
  isRunning: boolean;
}

export function RunControlPanel({ onStartRun, isRunning }: RunControlPanelProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Run Control</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">Execute robustness analysis</p>
        </div>
        {isRunning && (
          <span className="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400">
            <Loader2 className="w-4 h-4 animate-spin" />
            Running...
          </span>
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
          <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 mb-1">
            <Activity className="w-4 h-4" />
            <span className="text-xs">Status</span>
          </div>
          <p className="text-lg font-semibold text-slate-900 dark:text-white">
            {isRunning ? 'Running' : 'Ready'}
          </p>
        </div>
        <div className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
          <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 mb-1">
            <Cpu className="w-4 h-4" />
            <span className="text-xs">Runs</span>
          </div>
          <p className="text-lg font-semibold text-slate-900 dark:text-white">15</p>
        </div>
        <div className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
          <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 mb-1">
            <Clock className="w-4 h-4" />
            <span className="text-xs">Method</span>
          </div>
          <p className="text-lg font-semibold text-slate-900 dark:text-white">±10%</p>
        </div>
        <div className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
          <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 mb-1">
            <CheckCircle2 className="w-4 h-4" />
            <span className="text-xs">Params</span>
          </div>
          <p className="text-lg font-semibold text-slate-900 dark:text-white">3 active</p>
        </div>
      </div>

      {/* Start Button */}
      <button
        onClick={onStartRun}
        disabled={isRunning}
        className={cn(
          'w-full flex items-center justify-center gap-2 px-6 py-4 rounded-xl font-medium transition-all',
          isRunning
            ? 'bg-slate-100 dark:bg-slate-700 text-slate-400 cursor-not-allowed'
            : 'bg-slate-900 dark:bg-white text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-slate-100 hover:scale-[1.02]'
        )}
      >
        {isRunning ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Running Analysis...
          </>
        ) : (
          <>
            <Play className="w-5 h-5" />
            Start Robustness Analysis
          </>
        )}
      </button>
    </motion.div>
  );
}
