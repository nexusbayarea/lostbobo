import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Navigation } from '@/components/Navigation';
import { useAuth } from '@/hooks/useAuth';
import { supabase } from '@/lib/supabase';
import { BookOpen, Save, Clock, AlertCircle, CheckCircle2 } from 'lucide-react';

interface NotebookData {
  context: string;
  parameters: string;
  observations: string;
  hypotheses: string;
  nextExperiments: string;
  notes: string;
}

const defaultData: NotebookData = {
  context: '',
  parameters: '',
  observations: '',
  hypotheses: '',
  nextExperiments: '',
  notes: '',
};

const sections = [
  { title: 'Simulation Context', field: 'context' as const, height: 'h-32', placeholder: 'Describe the simulation goal, boundary conditions, and physical model...' },
  { title: 'Parameters', field: 'parameters' as const, height: 'h-28', placeholder: 'List solver settings, mesh resolution, time steps, material properties...' },
  { title: 'Observations', field: 'observations' as const, height: 'h-32', placeholder: 'Record convergence behavior, anomalies, thermal drift, pressure spikes...' },
  { title: 'Hypotheses', field: 'hypotheses' as const, height: 'h-28', placeholder: 'What do you think is driving the results? What would you test next?' },
  { title: 'Next Experiments', field: 'nextExperiments' as const, height: 'h-28', placeholder: 'Planned parameter sweeps, mesh refinements, or model changes...' },
  { title: 'Freeform Notes', field: 'notes' as const, height: 'h-40', placeholder: 'Any additional thoughts, references, or scratch work...' },
];

export function EngineerNotebook() {
  const { user } = useAuth();
  const [data, setData] = useState<NotebookData>(defaultData);
  const [status, setStatus] = useState<'saved' | 'saving' | 'error'>('saved');
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (!user?.id || !supabase) return;
    supabase
      .from('notebooks')
      .select('*')
      .eq('user_id', user.id)
      .single()
      .then(({ data: row, error }) => {
        if (row) {
          setData({
            context: row.context || '',
            parameters: row.parameters || '',
            observations: row.observations || '',
            hypotheses: row.hypotheses || '',
            nextExperiments: row.next_experiments || '',
            notes: row.notes || '',
          });
        }
        setLoaded(true);
      });
  }, [user?.id]);

  useEffect(() => {
    if (!user?.id || !supabase || !loaded) return;

    setStatus('saving');
    const timeout = setTimeout(() => {
      const client = supabase;
      if (!client) return;
      client
        .from('notebooks')
        .upsert({
          user_id: user.id,
          context: data.context,
          parameters: data.parameters,
          observations: data.observations,
          hypotheses: data.hypotheses,
          next_experiments: data.nextExperiments,
          notes: data.notes,
          updated_at: new Date().toISOString(),
        }, { onConflict: 'user_id' })
        .then(({ error }) => {
          if (error) {
            setStatus('error');
          } else {
            setStatus('saved');
          }
        });
    }, 1200);

    return () => clearTimeout(timeout);
  }, [data, user?.id, loaded]);

  const updateField = (field: keyof NotebookData, value: string) => {
    setData((prev) => ({ ...prev, [field]: value }));
  };

  const statusIcon = status === 'saved' ? (
    <CheckCircle2 className="w-4 h-4 text-green-400" />
  ) : status === 'saving' ? (
    <Clock className="w-4 h-4 text-yellow-400 animate-pulse" />
  ) : (
    <AlertCircle className="w-4 h-4 text-red-400" />
  );

  return (
    <div className="min-h-screen flex flex-col bg-background dark:bg-slate-950">
      <Navigation />
      <div className="flex-1 pt-[72px] p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <div className="flex items-center gap-3">
              <BookOpen className="w-8 h-8 text-cyan-400" />
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Engineer Notebook</h1>
            </div>
            <div className="flex items-center gap-2 text-sm">
              {statusIcon}
              <span className="text-slate-500 dark:text-slate-400 capitalize">{status}</span>
            </div>
          </div>

          {sections.map((section, index) => (
            <motion.div
              key={section.field}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.08 }}
              className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 mb-6 shadow-sm"
            >
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-3">{section.title}</h2>
              <textarea
                value={data[section.field]}
                onChange={(e) => updateField(section.field, e.target.value)}
                placeholder={section.placeholder}
                className={`w-full ${section.height} p-4 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent resize-y font-mono text-sm leading-relaxed`}
              />
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
