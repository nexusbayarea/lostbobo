import React from 'react';
import { X, FileText, Zap, Download, Activity } from 'lucide-react';
import type { SimulationRecord } from '@/hooks/useSimulationUpdates';

interface SimulationDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  simulation: SimulationRecord | null;
}

export const SimulationDetailModal = ({ isOpen, onClose, simulation }: SimulationDetailModalProps) => {
  if (!isOpen || !simulation) return null;

  const aiInsight = simulation.result_summary?.ai_insight || 
    "Simulation data processed. No structural anomalies detected in current iteration.";

  const metrics = simulation.result_summary?.metrics || { error: 'Pending analysis' };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="bg-[#0a0a0a] border border-[#00f2ff33] w-full max-w-2xl rounded-lg shadow-2xl overflow-hidden">
        <div className="flex justify-between items-center p-6 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <Activity className="text-[#00f2ff] w-6 h-6" />
            <h2 className="text-xl font-bold text-white">
              {simulation.scenario_name || 'Untitled Simulation'}
            </h2>
          </div>
          <button 
            onClick={onClose} 
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-[#111] rounded border border-gray-800">
              <span className="text-xs text-gray-500 uppercase">Status</span>
              <p className="text-[#00f2ff] font-mono capitalize">{simulation.status}</p>
            </div>
            <div className="p-4 bg-[#111] rounded border border-gray-800">
              <span className="text-xs text-gray-500 uppercase">Engine ID</span>
              <p className="text-gray-300 font-mono text-sm">
                {simulation.job_id?.substring(0, 12) || 'N/A'}...
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-[#111] rounded border border-gray-800">
              <span className="text-xs text-gray-500 uppercase">Created</span>
              <p className="text-gray-300 font-mono text-sm">
                {simulation.created_at ? new Date(simulation.created_at).toLocaleString() : 'N/A'}
              </p>
            </div>
            <div className="p-4 bg-[#111] rounded border border-gray-800">
              <span className="text-xs text-gray-500 uppercase">Report</span>
              <p className="text-gray-300 font-mono text-sm capitalize">
                {simulation.report_url ? 'Available' : 'Pending'}
              </p>
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="flex items-center gap-2 text-sm font-semibold text-gray-400">
              <Zap size={16} className="text-yellow-500" /> AI-GENERATED INSIGHTS
            </h3>
            <div className="p-4 bg-[#0d1b1d] border border-[#00f2ff11] rounded text-gray-300 text-sm leading-relaxed italic">
              {aiInsight}
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-gray-400 uppercase">Physics Summary</h3>
            <pre className="p-4 bg-black rounded text-[#00f2ff] text-xs font-mono overflow-x-auto border border-gray-900">
              {JSON.stringify(metrics, null, 2)}
            </pre>
          </div>
        </div>

        <div className="p-6 bg-[#0f0f0f] border-t border-gray-800 flex justify-end gap-4">
          {simulation.report_url && (
            <a 
              href={simulation.report_url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex items-center gap-2 bg-[#00f2ff] text-black px-4 py-2 rounded font-bold hover:bg-white transition-colors"
            >
              <FileText size={18} /> DOWNLOAD FULL PDF
            </a>
          )}
        </div>
      </div>
    </div>
  );
};
