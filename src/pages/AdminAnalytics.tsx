import React, { useEffect, useState } from 'react';
import { Activity, Users, Database, Cpu } from 'lucide-react';
import { supabase } from '@/lib/supabase';
import { useAuth } from '@/hooks/useAuth';

interface Stats {
  activeWorkers: number;
  totalJobs: number;
  uniqueUsers: number;
}

interface Lead {
  email: string;
  runs_completed: number;
  qualification: string;
  updated_at: string;
}

const StatCard = ({ icon, label, value, color }: { 
  icon: React.ReactNode; 
  label: string; 
  value: number; 
  color: string;
}) => (
  <div className="bg-[#0a0a0a] p-6 rounded-lg border border-gray-800">
    <div className={`${color} mb-2`}>{icon}</div>
    <div className="text-gray-500 text-xs uppercase font-bold">{label}</div>
    <div className="text-3xl font-mono mt-1">{value}</div>
  </div>
);

export const AdminAnalytics = () => {
  const { getToken, user } = useAuth();
  const [stats, setStats] = useState<Stats>({ activeWorkers: 0, totalJobs: 0, uniqueUsers: 0 });
  const [recentLeads, setRecentLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const fiveMinsAgo = new Date(Date.now() - 300000).toISOString();

        const [workersRes, jobsRes, leadsRes] = await Promise.all([
          supabase
            .from('worker_heartbeat')
            .select('*', { count: 'exact', head: true })
            .gt('last_ping', fiveMinsAgo),
          supabase
            .from('simulation_history')
            .select('*', { count: 'exact', head: true }),
          supabase
            .from('leads')
            .select('*')
            .order('updated_at', { ascending: false })
            .limit(10),
        ]);

        setStats({
          activeWorkers: workersRes.count || 0,
          totalJobs: jobsRes.count || 0,
          uniqueUsers: leadsRes.data?.length || 0,
        });
        setRecentLeads((leadsRes.data as Lead[]) || []);
      } catch (error) {
        console.error('Failed to load admin stats:', error);
      } finally {
        setLoading(false);
      }
    };

    loadStats();
  }, []);

  return (
    <div className="p-8 bg-[#050505] min-h-screen text-white">
      <h1 className="text-2xl font-bold mb-8 flex items-center gap-2">
        <Database className="text-[#00f2ff]" /> NexusBayArea Admin Control
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <StatCard 
          icon={<Cpu />} 
          label="Active GPU Pods" 
          value={stats.activeWorkers} 
          color="text-green-400" 
        />
        <StatCard 
          icon={<Activity />} 
          label="Total Simulations" 
          value={stats.totalJobs} 
          color="text-[#00f2ff]" 
        />
        <StatCard 
          icon={<Users />} 
          label="Identified Leads" 
          value={stats.uniqueUsers} 
          color="text-purple-400" 
        />
      </div>

      <div className="bg-[#0a0a0a] border border-gray-800 rounded-lg p-6">
        <h2 className="text-sm uppercase text-gray-500 mb-4 font-bold">Recent Alpha Activity</h2>
        {loading ? (
          <p className="text-gray-500 text-sm">Loading...</p>
        ) : recentLeads.length === 0 ? (
          <p className="text-gray-500 text-sm">No leads recorded yet.</p>
        ) : (
          <table className="w-full text-left">
            <thead>
              <tr className="text-gray-400 text-xs border-b border-gray-800">
                <th className="pb-3">User Email</th>
                <th className="pb-3">Runs</th>
                <th className="pb-3">Status</th>
                <th className="pb-3">Last Activity</th>
              </tr>
            </thead>
            <tbody className="text-sm">
              {recentLeads.map((lead, i) => (
                <tr key={`${lead.email}-${i}`} className="border-b border-gray-900">
                  <td className="py-4 text-gray-300">{lead.email}</td>
                  <td className="py-4 text-[#00f2ff] font-mono">{lead.runs_completed}</td>
                  <td className="py-4">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      lead.qualification === 'hot' 
                        ? 'bg-red-900/50 text-red-200 border border-red-800' 
                        : lead.qualification === 'warm'
                        ? 'bg-amber-900/50 text-amber-200 border border-amber-800'
                        : 'bg-blue-900/50 text-blue-200 border border-blue-800'
                    }`}>
                      {lead.qualification?.toUpperCase() || 'NEW'}
                    </span>
                  </td>
                  <td className="py-4 text-gray-500 font-mono text-xs">
                    {lead.updated_at ? new Date(lead.updated_at).toLocaleString() : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
