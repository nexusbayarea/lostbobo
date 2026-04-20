import React, { useState, useEffect } from 'react';
import { useSimulations } from '../../hooks/useSimulations';
import { useAuth } from '../../hooks/useAuth';
import { supabase } from '../../lib/supabase';
import { Activity, Users, Settings } from 'lucide-react';

const AdminAnalyticsPage = () => {
  const { user } = useAuth();
  const { simulations, loading } = useSimulations(user?.id || ''); 
  
  const [activeTab, setActiveTab] = useState('fleet_analytics');
  const [fleetMetrics, setFleetMetrics] = useState({ active_pods: 0, hourly_spend_usd: '0.00', active_simulations: 0 });

  useEffect(() => {
    const fetchMetrics = async () => {
      const { data, error } = await supabase.functions.invoke('get-fleet-metrics');
      if (data) {
        setFleetMetrics(data);
      } else if (error) {
        console.error("Failed to fetch fleet metrics:", error);
      }
    };

    fetchMetrics();
    const intervalId = setInterval(fetchMetrics, 60000);
    return () => clearInterval(intervalId);
  }, []);

  const queuedSims = simulations.filter(sim => sim.status === 'queued').length;

  return (
    <div className="admin-layout flex h-screen bg-background text-foreground transition-colors duration-300">
      
      <aside className="w-64 bg-sidebar border-r border-sidebar-border p-4 flex flex-col">
        <h2 className="text-xl font-bold text-primary mb-8 px-2">Mercury Admin</h2>
        <nav className="flex-1 space-y-2">
          <button 
            onClick={() => setActiveTab('fleet_analytics')}
            className={`w-full text-left px-4 py-2 rounded flex items-center gap-3 ${activeTab === 'fleet_analytics' ? 'bg-accent text-accent-foreground' : 'hover:bg-accent/50'}`}
          >
            <Activity size={18} /> Fleet Analytics
          </button>
          <button className="w-full text-left px-4 py-2 rounded flex items-center gap-3 text-muted-foreground cursor-not-allowed">
            <Users size={18} /> User Management
          </button>
        </nav>

        <div className="mt-auto pt-4 border-t border-sidebar-border">
          <div className="flex items-center gap-2 px-2 py-3 bg-primary/5 rounded-lg border border-primary/10">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-[11px] font-mono uppercase tracking-widest opacity-70">
              System Live: 8080
            </span>
          </div>
        </div>
      </aside>

      <main className="flex-1 p-8 overflow-y-auto">
        
        {activeTab === 'fleet_analytics' && (
          <div className="space-y-8">
            <header className="flex justify-between items-end">
              <div>
                <h1 className="text-3xl font-bold">Fleet Analytics</h1>
                <p className="text-muted-foreground">Real-time margin tracking and worker telemetry.</p>
              </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-card p-6 rounded-lg border border-border shadow-sm">
                <h3 className="text-muted-foreground text-sm">Active Workers</h3>
                <p className="text-4xl font-bold mt-2">{fleetMetrics.active_pods}</p>
              </div>
              <div className="bg-card p-6 rounded-lg border border-border shadow-sm">
                <h3 className="text-muted-foreground text-sm">Compute Burn Rate</h3>
                <p className="text-4xl font-bold text-destructive mt-2">${fleetMetrics.hourly_spend_usd} <span className="text-lg text-foreground">/hr</span></p>
              </div>
              <div className="bg-card p-6 rounded-lg border border-border shadow-sm">
                <h3 className="text-muted-foreground text-sm">Active Simulations</h3>
                <p className="text-4xl font-bold text-primary mt-2">{fleetMetrics.active_simulations}</p>
              </div>
              <div className="bg-card p-6 rounded-lg border border-border shadow-sm">
                <h3 className="text-muted-foreground text-sm">Queue Depth</h3>
                <p className="text-4xl font-bold text-amber-500 mt-2">{queuedSims}</p>
              </div>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border shadow-sm min-h-[400px]">
              <h3 className="text-xl font-bold mb-4">Live GPU Telemetry</h3>
              {loading ? (
                <div className="text-muted-foreground animate-pulse">Syncing with Mercury AI...</div>
              ) : (
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-border text-muted-foreground">
                      <th className="py-3 font-medium">Job ID</th>
                      <th className="py-3 font-medium">Status</th>
                      <th className="py-3 font-medium">Progress</th>
                    </tr>
                  </thead>
                  <tbody>
                    {simulations.slice(0, 5).map(sim => (
                      <tr key={sim.id} className="border-b border-border">
                        <td className="py-4 font-mono text-sm">{sim.job_id.substring(0, 8)}...</td>
                        <td className="py-4">
                          <span className={`px-2 py-1 rounded text-xs ${sim.status === 'processing' ? 'bg-primary/20 text-primary' : 'bg-secondary text-secondary-foreground'}`}>
                            {sim.status}
                          </span>
                        </td>
                        <td className="py-4">
                          <div className="w-full bg-secondary rounded-full h-2 max-w-[200px]">
                            <div className="bg-primary h-2 rounded-full transition-all duration-500" style={{ width: `${sim.progress}%` }}></div>
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
