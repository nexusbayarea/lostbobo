import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Cpu, Shield, Zap } from 'lucide-react';
import { Navigation } from '@/components/Navigation';
import { SimHPCLogo } from '@/components/SimHPCLogo';

export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-slate-950">
      <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/5 via-transparent to-transparent" />
      <div className="relative z-10 max-w-7xl mx-auto px-4 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <SimHPCLogo className="w-24 h-24 mx-auto mb-8" />
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
            SimHPC <span className="text-cyan-400">Mission Control</span>
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10">
            AI-powered Monte Carlo simulation platform for aerospace and thermal engineering.
            Run robustness analysis on GPU clusters with Mercury AI assistance.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link
              to="/dashboard"
              className="flex items-center gap-2 px-8 py-4 bg-cyan-500 hover:bg-cyan-600 text-white font-semibold rounded-2xl transition-colors"
            >
              Launch Dashboard <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              to="/signup"
              className="flex items-center gap-2 px-8 py-4 bg-slate-800 hover:bg-slate-700 text-white font-semibold rounded-2xl transition-colors border border-slate-700"
            >
              Get Started Free
            </Link>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto"
        >
          {[
            { icon: Cpu, title: 'GPU Clusters', desc: 'RunPod-powered compute' },
            { icon: Shield, title: 'Robustness Analysis', desc: 'Monte Carlo simulations' },
            { icon: Zap, title: 'Mercury AI', desc: 'AI-assisted engineering' },
          ].map((feature, i) => (
            <div key={i} className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <feature.icon className="w-8 h-8 text-cyan-400 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-white mb-1">{feature.title}</h3>
              <p className="text-slate-400 text-sm">{feature.desc}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
