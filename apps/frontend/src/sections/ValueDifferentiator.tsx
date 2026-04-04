import { motion } from 'framer-motion';
import { CheckCircle } from 'lucide-react';

const features = [
  'Monte Carlo robustness analysis',
  'GPU-accelerated physics simulations',
  'AI-assisted parameter optimization',
  'Real-time telemetry & monitoring',
  'PDF engineering reports',
  'Team collaboration',
];

export function ValueDifferentiator() {
  return (
    <section className="py-24 bg-slate-900">
      <div className="max-w-7xl mx-auto px-4 grid md:grid-cols-2 gap-12 items-center">
        <div>
          <h2 className="text-3xl font-bold text-white mb-6">Why SimHPC?</h2>
          <p className="text-slate-400 mb-8">
            Traditional simulation tools are slow and require expensive local hardware.
            SimHPC provides cloud GPU clusters with AI assistance, making robustness
            analysis accessible and affordable.
          </p>
          <div className="space-y-4">
            {features.map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                viewport={{ once: true }}
                className="flex items-center gap-3"
              >
                <CheckCircle className="w-5 h-5 text-cyan-400 flex-shrink-0" />
                <span className="text-slate-300">{feature}</span>
              </motion.div>
            ))}
          </div>
        </div>
        <div className="bg-slate-950 border border-slate-800 rounded-2xl p-8">
          <div className="space-y-4">
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Simulation Speed</span>
              <span className="text-cyan-400 font-bold">10x Faster</span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-2">
              <div className="bg-cyan-400 h-2 rounded-full" style={{ width: '90%' }} />
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Cost Efficiency</span>
              <span className="text-cyan-400 font-bold">70% Lower</span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-2">
              <div className="bg-cyan-400 h-2 rounded-full" style={{ width: '70%' }} />
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">AI Assistance</span>
              <span className="text-cyan-400 font-bold">Built-in</span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-2">
              <div className="bg-cyan-400 h-2 rounded-full" style={{ width: '100%' }} />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
