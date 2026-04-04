import { motion } from 'framer-motion';
import { Users, Cpu, Building2 } from 'lucide-react';

const audiences = [
  {
    icon: Users,
    title: 'Engineers',
    desc: 'Run robustness analysis without expensive local hardware',
  },
  {
    icon: Cpu,
    title: 'Researchers',
    desc: 'GPU-accelerated Monte Carlo simulations for academic work',
  },
  {
    icon: Building2,
    title: 'Enterprises',
    desc: 'Team collaboration, API access, and dedicated compute',
  },
];

export function WhoItsFor() {
  return (
    <section className="py-24 bg-slate-950">
      <div className="max-w-7xl mx-auto px-4">
        <h2 className="text-3xl font-bold text-white text-center mb-12">Who It's For</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {audiences.map((item, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              viewport={{ once: true }}
              className="bg-slate-900 border border-slate-800 rounded-2xl p-8"
            >
              <item.icon className="w-10 h-10 text-cyan-400 mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">{item.title}</h3>
              <p className="text-slate-400">{item.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
