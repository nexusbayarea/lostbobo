import React from 'react';
import { Zap, Shield, PlayCircle, X } from 'lucide-react';

export const WelcomeOverlay = ({ onClose }: { onClose: () => void }) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="max-w-md w-full bg-gray-900 border border-gray-800 rounded-2xl p-8 shadow-2xl relative overflow-hidden">
        {/* Decorative background glow */}
        <div className="absolute -top-24 -left-24 w-48 h-48 bg-cyan-500/10 rounded-full blur-3xl" />
        
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-500 hover:text-white">
          <X size={20} />
        </button>

        <div className="relative">
          <div className="h-12 w-12 bg-cyan-500/20 rounded-lg flex items-center justify-center mb-6">
            <Zap className="text-cyan-400" size={24} />
          </div>

          <h2 className="text-2xl font-bold text-white mb-2">Welcome to SimHPC</h2>
          <p className="text-gray-400 mb-8 leading-relaxed">
            We've provisioned <span className="text-white font-bold">10 Credits</span> and a 
            <span className="text-white font-bold"> Sample Result</span> to get you started.
          </p>

          <div className="space-y-4 mb-8">
            <div className="flex gap-4 items-start">
              <div className="mt-1 text-emerald-400"><Shield size={18} /></div>
              <div>
                <p className="text-sm font-semibold text-gray-200">Certified Results</p>
                <p className="text-xs text-gray-500">Every run generates a SHA-256 verifiable certificate.</p>
              </div>
            </div>
            <div className="flex gap-4 items-start">
              <div className="mt-1 text-cyan-400"><PlayCircle size={18} /></div>
              <div>
                <p className="text-sm font-semibold text-gray-200">Beta Fleet Access</p>
                <p className="text-xs text-gray-500">Deploy solvers across our high-performance GPU cluster.</p>
              </div>
            </div>
          </div>

          <button 
            onClick={onClose}
            className="w-full py-3 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl font-bold transition-all transform active:scale-95"
          >
            Launch My First Simulation
          </button>
        </div>
      </div>
    </div>
  );
};
