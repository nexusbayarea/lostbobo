import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Play,
  BarChart3,
  FileText,
  Settings,
  LogOut,
  Menu,
  X,
  Cpu,
  Loader2,
} from 'lucide-react';
import { ThemeToggle } from '@/components/ThemeToggle';
import { cn } from '@/lib/utils';
import { ConfigurationPanel } from '@/sections/dashboard/ConfigurationPanel';
import { RunControlPanel } from '@/sections/dashboard/RunControlPanel';
import { ResultsPanel } from '@/sections/dashboard/ResultsPanel';

const sidebarItems = [
  { id: 'simulations', label: 'Simulations', icon: Play },
  { id: 'robustness', label: 'Robustness', icon: BarChart3 },
  { id: 'reports', label: 'Reports', icon: FileText },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export function Dashboard() {
  const [activeTab, setActiveTab] = useState('robustness');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [currentRun, setCurrentRun] = useState<any>(null);
  const [isRunning, setIsRunning] = useState(false);

  const handleStartRun = () => {
    setIsRunning(true);
    // Simulate run
    setTimeout(() => {
      setIsRunning(false);
      setCurrentRun({
        id: 'run-001',
        status: 'completed',
        progress: 100,
        results: {
          baselineResult: {
            maxTemperature: 412.3,
            minTemperature: 289.4,
            peakStress: 125.8,
            convergenceTime: 48.2,
            meshElements: 2100000,
            residualTolerance: 1e-6,
          },
          sensitivityRanking: [
            { parameterName: 'boundary_flux', influenceCoefficient: 0.62, varianceContribution: 0.45, rank: 1 },
            { parameterName: 'thermal_conductivity', influenceCoefficient: 0.21, varianceContribution: 0.28, rank: 2 },
            { parameterName: 'ambient_temp', influenceCoefficient: 0.09, varianceContribution: 0.12, rank: 3 },
          ],
          confidenceInterval: 3.1,
          variance: 142.3,
          runCount: 15,
        },
      });
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex">
      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: isSidebarOpen ? 280 : 80 }}
        transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
        className={cn(
          'fixed left-0 top-0 bottom-0 z-40 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700',
          !isSidebarOpen && 'items-center'
        )}
      >
        {/* Logo */}
        <div className="h-[72px] flex items-center px-6 border-b border-slate-200 dark:border-slate-700">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 flex-shrink-0">
              <svg viewBox="0 0 48 48" fill="none" className="w-full h-full">
                <path d="M24 2L44 13.5V36.5L24 48L4 36.5V13.5L24 2Z" className="stroke-slate-900 dark:stroke-white" strokeWidth="2" />
                <path d="M24 2V48M4 13.5L44 36.5M44 13.5L4 36.5" className="stroke-slate-900 dark:stroke-white" strokeWidth="1.5" strokeOpacity="0.6" />
                <circle cx="24" cy="25" r="4" className="fill-blue-500" />
              </svg>
            </div>
            <AnimatePresence>
              {isSidebarOpen && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="font-bold text-xl text-slate-900 dark:text-white whitespace-nowrap"
                >
                  Sim<span className="text-blue-500">HPC</span>
                </motion.span>
              )}
            </AnimatePresence>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          {sidebarItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={cn(
                'w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all',
                activeTab === item.id
                  ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700',
                !isSidebarOpen && 'justify-center px-2'
              )}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              <AnimatePresence>
                {isSidebarOpen && (
                  <motion.span
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="font-medium whitespace-nowrap"
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>
            </button>
          ))}
        </nav>

        {/* Bottom Actions */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-200 dark:border-slate-700">
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className={cn(
              'w-full flex items-center gap-3 px-4 py-3 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-xl transition-all',
              !isSidebarOpen && 'justify-center px-2'
            )}
          >
            {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            <AnimatePresence>
              {isSidebarOpen && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="font-medium whitespace-nowrap"
                >
                  Collapse
                </motion.span>
              )}
            </AnimatePresence>
          </button>
          <button
            className={cn(
              'w-full flex items-center gap-3 px-4 py-3 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-all mt-2',
              !isSidebarOpen && 'justify-center px-2'
            )}
          >
            <LogOut className="w-5 h-5" />
            <AnimatePresence>
              {isSidebarOpen && (
                <motion.span
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="font-medium whitespace-nowrap"
                >
                  Sign Out
                </motion.span>
              )}
            </AnimatePresence>
          </button>
        </div>
      </motion.aside>

      {/* Main Content */}
      <main
        className={cn(
          'flex-1 min-h-screen transition-all duration-300',
          isSidebarOpen ? 'ml-[280px]' : 'ml-[80px]'
        )}
      >
        {/* Header */}
        <header className="h-[72px] bg-white/80 dark:bg-slate-800/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-700 sticky top-0 z-30 px-8 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-semibold text-slate-900 dark:text-white capitalize">
              {activeTab}
            </h1>
            {isRunning && (
              <span className="flex items-center gap-2 text-sm text-blue-600 dark:text-blue-400">
                <Loader2 className="w-4 h-4 animate-spin" />
                Running simulation...
              </span>
            )}
          </div>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-medium">
              JD
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="p-8">
          {activeTab === 'robustness' && (
            <div className="space-y-8">
              <ConfigurationPanel />
              <RunControlPanel onStartRun={handleStartRun} isRunning={isRunning} />
              {currentRun && <ResultsPanel run={currentRun} />}
            </div>
          )}

          {activeTab === 'simulations' && (
            <div className="text-center py-16">
              <Cpu className="w-16 h-16 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                Simulation Library
              </h2>
              <p className="text-slate-500 dark:text-slate-400">
                Your saved simulations will appear here.
              </p>
            </div>
          )}

          {activeTab === 'reports' && (
            <div className="text-center py-16">
              <FileText className="w-16 h-16 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                AI Reports
              </h2>
              <p className="text-slate-500 dark:text-slate-400">
                Your generated reports will appear here.
              </p>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="max-w-2xl">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-6">
                Account Settings
              </h2>
              <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 space-y-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Display Name
                  </label>
                  <input
                    type="text"
                    defaultValue="John Doe"
                    className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    defaultValue="john@company.com"
                    className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Company
                  </label>
                  <input
                    type="text"
                    defaultValue="Acme Engineering"
                    className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <button className="px-6 py-3 bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-medium rounded-xl hover:bg-slate-800 dark:hover:bg-slate-100 transition-colors">
                  Save Changes
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
