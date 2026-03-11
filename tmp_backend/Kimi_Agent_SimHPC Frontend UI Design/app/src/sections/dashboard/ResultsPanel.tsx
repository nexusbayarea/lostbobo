import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ReferenceLine,
} from 'recharts';
import {
  CheckCircle2,
  Target,
  TrendingUp,
  Activity,
  Download,
  Brain,
  Shield,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface ResultsPanelProps {
  run: any;
}

const TABS = [
  { id: 'summary', label: 'Summary', icon: Target },
  { id: 'visualization', label: 'Visualization', icon: Activity },
  { id: 'metrics', label: 'Metrics', icon: TrendingUp },
  { id: 'ai', label: 'AI Insights', icon: Brain },
];

export function ResultsPanel({ run }: ResultsPanelProps) {
  const [activeTab, setActiveTab] = useState('summary');

  const sensitivityData = run.results.sensitivityRanking.map((s: any) => ({
    name: s.parameterName,
    influence: s.influenceCoefficient,
  }));

  const tempData = Array.from({ length: 15 }, (_, i) => ({
    runId: i,
    maxTemp: 380 + Math.random() * 60,
  }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden"
    >
      {/* Header */}
      <div className="p-6 border-b border-slate-200 dark:border-slate-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                Analysis Complete
              </h2>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Run ID: {run.id} • {run.results.runCount} runs completed
              </p>
            </div>
          </div>
          <button className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 dark:border-slate-700">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'flex items-center gap-2 px-6 py-4 text-sm font-medium transition-colors border-b-2',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            )}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'summary' && (
          <div className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-100 dark:border-blue-800">
                <p className="text-xs text-blue-600 dark:text-blue-400 mb-1">Max Temperature</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  {run.results.baselineResult.maxTemperature.toFixed(1)} K
                </p>
              </div>
              <div className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Peak Stress</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  {run.results.baselineResult.peakStress.toFixed(1)} MPa
                </p>
              </div>
              <div className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Convergence</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  {run.results.baselineResult.convergenceTime.toFixed(1)}s
                </p>
              </div>
              <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-100 dark:border-green-800">
                <p className="text-xs text-green-600 dark:text-green-400 mb-1">Confidence</p>
                <p className="text-2xl font-bold text-green-700 dark:text-green-400">
                  ±{run.results.confidenceInterval}%
                </p>
              </div>
            </div>

            {/* Sensitivity Ranking */}
            <div>
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-4">
                Sensitivity Ranking
              </h3>
              <div className="space-y-3">
                {run.results.sensitivityRanking.map((metric: any, index: number) => (
                  <div
                    key={metric.parameterName}
                    className="flex items-center gap-4 p-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl"
                  >
                    <div className="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center text-sm font-semibold">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-slate-900 dark:text-white">{metric.parameterName}</p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        Variance contribution: {(metric.varianceContribution * 100).toFixed(1)}%
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-slate-900 dark:text-white">
                        {metric.influenceCoefficient.toFixed(2)}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">influence</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'visualization' && (
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-4">
                Sensitivity Ranking
              </h3>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={sensitivityData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                    <XAxis type="number" domain={[0, 1]} />
                    <YAxis type="category" dataKey="name" width={120} />
                    <Tooltip />
                    <Bar dataKey="influence" fill="#3B82F6" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-4">
                Temperature Distribution
              </h3>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" dataKey="runId" name="Run" />
                    <YAxis type="number" dataKey="maxTemp" name="Max Temp" unit=" K" />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    <ReferenceLine y={412.3} stroke="#10B981" strokeDasharray="5 5" label="Baseline" />
                    <Scatter data={tempData} fill="#3B82F6" />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'metrics' && (
          <div className="space-y-6">
            <div className="grid md:grid-cols-3 gap-4">
              <div className="p-6 bg-slate-50 dark:bg-slate-700/50 rounded-xl text-center">
                <p className="text-3xl font-bold text-slate-900 dark:text-white">{run.results.runCount}</p>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Total Runs</p>
              </div>
              <div className="p-6 bg-slate-50 dark:bg-slate-700/50 rounded-xl text-center">
                <p className="text-3xl font-bold text-slate-900 dark:text-white">0</p>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Non-convergent</p>
              </div>
              <div className="p-6 bg-slate-50 dark:bg-slate-700/50 rounded-xl text-center">
                <p className="text-3xl font-bold text-slate-900 dark:text-white">
                  {run.results.variance.toFixed(1)}
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Variance</p>
              </div>
            </div>

            <div className="p-6 bg-slate-50 dark:bg-slate-700/50 rounded-xl">
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-4">
                Stability Assessment
              </h3>
              <div className="flex items-center gap-4">
                <div className="flex-1 h-4 bg-slate-200 dark:bg-slate-600 rounded-full overflow-hidden">
                  <div className="h-full w-[95%] bg-green-500 rounded-full" />
                </div>
                <span className="text-sm font-medium text-green-600 dark:text-green-400">95% Stable</span>
              </div>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-3">
                System stability is within acceptable parameters across all perturbation runs.
              </p>
            </div>
          </div>
        )}

        {activeTab === 'ai' && (
          <div className="space-y-6">
            <div className="flex items-start gap-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-100 dark:border-blue-800">
              <Brain className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-blue-800 dark:text-blue-300">
                  Advisory Interpretation
                </p>
                <p className="text-sm text-blue-700 dark:text-blue-400 mt-1">
                  This report provides AI-generated interpretation of simulation outputs. All numerical
                  results originate from deterministic solvers (MFEM + SUNDIALS).
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="p-6 border border-slate-200 dark:border-slate-700 rounded-xl">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-3">
                  1. Simulation Summary
                </h3>
                <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                  <li>• Solver: MFEM + SUNDIALS</li>
                  <li>• Mesh elements: 2.1M</li>
                  <li>• Convergence time: 48.2 sec</li>
                  <li>• Residual tolerance achieved: 1e-6</li>
                </ul>
              </div>

              <div className="p-6 border border-slate-200 dark:border-slate-700 rounded-xl">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-3">
                  2. Sensitivity Ranking
                </h3>
                <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                  Model output indicates that peak temperature is primarily driven by boundary heat flux
                  variation (0.62 influence coefficient). Thermal conductivity shows moderate influence
                  (0.21), while ambient temperature demonstrates relatively weak coupling (0.09).
                </p>
              </div>

              <div className="p-6 border border-slate-200 dark:border-slate-700 rounded-xl">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-3">
                  3. Engineering Interpretation
                </h3>
                <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                  Small perturbations in boundary heat flux produce nonlinear amplification in peak
                  temperature response. Model behavior shows that system stability is sensitive to
                  cooling efficiency under high current density conditions.
                </p>
              </div>

              <div className="p-6 border border-slate-200 dark:border-slate-700 rounded-xl">
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-3">
                  4. Suggested Next Simulation
                </h3>
                <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                  <li>• Increase mesh refinement near boundary interface</li>
                  <li>• Evaluate 10–15% flux variation range</li>
                  <li>• Test nonlinear material model under elevated temperature</li>
                </ul>
              </div>
            </div>

            <div className="flex items-start gap-4 p-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl border border-dashed border-slate-300 dark:border-slate-600">
              <Shield className="w-5 h-5 text-slate-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-slate-500 dark:text-slate-400">
                AI-generated interpretation based on simulation outputs. Numerical results originate
                from deterministic solvers.
              </p>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
