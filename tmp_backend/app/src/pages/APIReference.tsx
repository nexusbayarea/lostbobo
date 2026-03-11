import { PageLayout } from '@/components/PageLayout';
import { Terminal } from 'lucide-react';

export function APIReference() {
    return (
        <PageLayout>
            <div className="pt-32 pb-20 px-6 max-w-4xl mx-auto">
                <h1 className="text-4xl font-bold mb-6 text-slate-900 dark:text-white">API Reference</h1>
                <p className="text-slate-600 dark:text-slate-400 mb-8">REST endpoints for automation.</p>
                <pre className="bg-slate-900 text-slate-300 p-4 rounded-xl overflow-x-auto">
                    {`curl -X POST https://api.simhpc.com/v1/simulations \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "mesh_id": "m_9428",
    "solver": "mfem"
  }'`}
                </pre>
            </div>
        </PageLayout>
    );
}
