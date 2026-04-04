import { Link } from 'react-router-dom';
import { Cpu } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-slate-950 border-t border-slate-800 py-12">
      <div className="max-w-7xl mx-auto px-4 grid md:grid-cols-4 gap-8">
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Cpu className="w-6 h-6 text-cyan-400" />
            <span className="text-lg font-bold text-white">SimHPC</span>
          </div>
          <p className="text-slate-400 text-sm">
            AI-powered Monte Carlo simulation platform for aerospace and thermal engineering.
          </p>
        </div>
        <div>
          <h4 className="text-sm font-semibold text-white mb-4">Product</h4>
          <ul className="space-y-2">
            <li><Link to="/dashboard" className="text-slate-400 hover:text-white text-sm">Dashboard</Link></li>
            <li><Link to="/signup" className="text-slate-400 hover:text-white text-sm">Pricing</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="text-sm font-semibold text-white mb-4">Legal</h4>
          <ul className="space-y-2">
            <li><Link to="/terms" className="text-slate-400 hover:text-white text-sm">Terms</Link></li>
            <li><Link to="/privacy" className="text-slate-400 hover:text-white text-sm">Privacy</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="text-sm font-semibold text-white mb-4">Resources</h4>
          <ul className="space-y-2">
            <li><a href="#" className="text-slate-400 hover:text-white text-sm">Documentation</a></li>
            <li><a href="#" className="text-slate-400 hover:text-white text-sm">API Reference</a></li>
          </ul>
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-4 mt-8 pt-8 border-t border-slate-800 text-center text-slate-500 text-sm">
        © 2026 SimHPC. All rights reserved.
      </div>
    </footer>
  );
}
