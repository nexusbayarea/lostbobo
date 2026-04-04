import { motion } from 'framer-motion';
import { Cpu, Database, Cloud, Shield } from 'lucide-react';

const stack = [
  { icon: Cpu, name: 'RunPod GPU', desc: 'NVIDIA A40/A100 clusters' },
  { icon: Database, name: 'Redis Queue', desc: 'Job orchestration & scaling' },
  { icon: Cloud, name: 'FastAPI Backend', desc: 'Mercury AI integration' },
  { icon: Shield, name: 'Supabase', desc: 'Auth, DB & Realtime' },
];

export function Stack() {
  return (
    <section className="py-24 bg-slate-950">
      <div className="max-w-7xl mx-auto px-4">
        <h2 className="text-3xl font-bold text-white text-center mb-12">Technology Stack</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {stack.map((item, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              viewport={{ once: true }}
              className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-center"
            >
              <item.icon className="w-10 h-10 text-cyan-400 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-white mb-1">{item.name}</h3>
              <p className="text-slate-400 text-sm">{item.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
