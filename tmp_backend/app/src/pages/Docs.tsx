import { PageLayout } from '@/components/PageLayout';
import { Book } from 'lucide-react';

export function Docs() {
    return (
        <PageLayout>
            <div className="pt-32 pb-20 px-6 max-w-4xl mx-auto">
                <h1 className="text-4xl font-bold mb-6 text-slate-900 dark:text-white">Documentation</h1>
                <p className="text-slate-600 mb-8 dark:text-slate-400">Everything you need to configure and run simulations.</p>
                <div className="space-y-4 text-slate-800 dark:text-slate-200">
                    <h2 className="text-2xl font-semibold">SUNDIALS Integration</h2>
                    <p>Differential and algebraic equation solvers for time-dependent physics.</p>
                    <h2 className="text-2xl font-semibold mt-6">MFEM Library</h2>
                    <p>High-order finite element element library for scalable physics simulations.</p>
                </div>
            </div>
        </PageLayout>
    );
}
