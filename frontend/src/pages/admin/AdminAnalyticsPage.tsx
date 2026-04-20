import React, { useState } from 'react';
import { useSimulations } from '../../hooks/useSimulations';
import { useAuth } from '../../hooks/useAuth';

const AdminAnalyticsPage = () => {
  const { user } = useAuth();
  // Using a dummy user id for now; implement proper admin fetch logic if needed
  const { simulations, loading } = useSimulations(user?.id || ''); 
  
  const [activeTab, setActiveTab] = useState('fleet_analytics');

  const activeSims = simulations.filter(sim => sim.status === 'processing').length;
  const queuedSims = simulations.filter(sim => sim.status === 'queued').length;
  
  const activeRunPods = Math.ceil(activeSims / 2);
  const hourlySpend = (activeRunPods * 0.44).toFixed(2);

  return (
    <div className="admin-layout flex h-screen bg-gray-900 text-white">
      
      <aside className="w-64 bg-gray-800 border-r border-gray-700 p-4 flex flex-col">
        <h2 className="text-xl font-bold text-cyan-400 mb-8">Mercury Admin</h2>
        <nav className="flex-1 space-y-2">
          <button 
            onClick={() => setActiveTab('fleet_analytics')}
            className={`w-full text-left px-4 py-2 rounded ${activeTab === 'fleet_analytics' ? 'bg-cyan-900 text-cyan-300' : 'hover:bg-gray-700'}`}
          >
            📊 Fleet Analytics
          </button>
          <button className="w-full text-left px-4 py-2 rounded text-gray-500 cursor-not-allowed">
            👥 User Management
          </button>
        </nav>
        <div className="text-sm text-gray-500 border-t border-gray-700 pt-4">
          Logged in as: Founder
        </div>
      </aside>

      <main className="flex-1 p-8 overflow-y-auto">
        
        {activeTab === 'fleet_analytics' && (
          <div className="space-y-8">
            <header className="flex justify-between items-end">
              <div>
                <h1 className="text-3xl font-bold">Fleet Analytics</h1>
                <p className="text-gray-400">Real-time margin tracking and worker telemetry.</p>
              </div>
              <div className="text-right">
                <span className="text-sm text-gray-400 uppercase tracking-widest">Platform Status</span>
                <div className="text-green-400 font-mono">🟢 All Systems Operational</div>
              </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <h3 className="text-gray-400 text-sm">Active Workers (RunPod)</h3>
                <p className="text-4xl font-bold text-white mt-2">{activeRunPods}</p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <h3 className="text-gray-400 text-sm">Compute Burn Rate</h3>
                <p className="text-4xl font-bold text-red-400 mt-2">${hourlySpend} <span className="text-lg">/hr</span></p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <h3 className="text-gray-400 text-sm">Active Simulations</h3>
                <p className="text-4xl font-bold text-cyan-400 mt-2">{activeSims}</p>
              </div>
              <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <h3 className="text-gray-400 text-sm">Queue Depth</h3>
                <p className="text-4xl font-bold text-yellow-400 mt-2">{queuedSims}</p>
              </div>
            </div>

            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 min-h-[400px]">
              <h3 className="text-xl font-bold mb-4">Live GPU Telemetry</h3>
              {loading ? (
                <div className="text-gray-500 animate-pulse">Syncing with Mercury AI...</div>
              ) : (
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-gray-700 text-gray-400">
                      <th className="py-3 font-medium">Job ID</th>
                      <th className="py-3 font-medium">Status</th>
                      <th className="py-3 font-medium">Progress</th>
                    </tr>
                  </thead>
                  <tbody>
                    {simulations.slice(0, 5).map(sim => (
                      <tr key={sim.id} className="border-b border-gray-750">
                        <td className="py-4 font-mono text-sm">{sim.job_id.substring(0, 8)}...</td>
                        <td className="py-4">
                          <span className={`px-2 py-1 rounded text-xs ${sim.status === 'processing' ? 'bg-cyan-900 text-cyan-300' : 'bg-gray-700 text-gray-300'}`}>
                            {sim.status}
                          </span>
                        </td>
                        <td className="py-4">
                          <div className="w-full bg-gray-700 rounded-full h-2 max-w-[200px]">
                            <div className="bg-cyan-400 h-2 rounded-full" style={{ width: `${sim.progress}%` }}></div>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AdminAnalyticsPage;
