import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { toast } from 'sonner';

export interface SimulationRecord {
  id: string;
  user_id: string;
  job_id: string;
  scenario_name: string;
  status: 'queued' | 'processing' | 'running' | 'completed' | 'failed';
  result_summary: Record<string, any> | null;
  report_url: string | null;
  created_at: string;
}

/**
 * Supabase Realtime hook for simulation history.
 * Listens for UPDATE events on the simulation_history table
 * so the dashboard reflects job status changes instantly.
 */
export const useSimulationUpdates = (userId: string | undefined) => {
  const [simulations, setSimulations] = useState<SimulationRecord[]>([]);

  useEffect(() => {
    if (!userId) return;

    // 1. Initial fetch of history
    const fetchHistory = async () => {
      const { data, error } = await supabase
        .from('simulation_history')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
        .limit(20);

      if (error) {
        console.error('Failed to fetch simulation history:', error);
        return;
      }
      if (data) setSimulations(data as SimulationRecord[]);
    };

    fetchHistory();

    // 2. Setup Realtime Subscription
    const channel = supabase
      .channel('simulation-updates')
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'simulation_history',
          filter: `user_id=eq.${userId}`,
        },
        (payload) => {
          const updated = payload.new as SimulationRecord;

          // Update local state so the table row changes instantly
          setSimulations((current) =>
            current.map((sim) => (sim.id === updated.id ? updated : sim))
          );

          // Trigger a prominent "Completion" toast at top-center
          if (updated.status === 'completed') {
            toast.success(`Simulation ${updated.scenario_name || updated.job_id.slice(0, 8)} Complete!`, {
              duration: 10000,
              description: 'Results are ready for review. Download your AI report below.',
              style: {
                minWidth: '380px',
                fontSize: '16px',
              },
            });
          }

          // Notify on failure
          if (updated.status === 'failed') {
            toast.error(`Simulation ${updated.scenario_name || updated.job_id.slice(0, 8)} Failed`, {
              duration: 10000,
              description: 'Check the job logs for details.',
            });
          }
        }
      )
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'simulation_history',
          filter: `user_id=eq.${userId}`,
        },
        (payload) => {
          const newSim = payload.new as SimulationRecord;
          setSimulations((current) => [newSim, ...current]);
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [userId]);

  return { simulations, setSimulations };
};
