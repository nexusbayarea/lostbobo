import { PageLayout } from '@/components/PageLayout';
import { FileText } from 'lucide-react';

export function DPA() {
    return (
        <PageLayout>
            <div className="pt-32 pb-20 px-6 max-w-4xl mx-auto">
                <h1 className="text-4xl font-bold mb-6 text-slate-900 dark:text-white">Data Processing Addendum</h1>
                <p className="text-slate-600 dark:text-slate-400 mb-8">
                    Standard Contractual Clauses & Data Safety
                </p>
                <p className="text-slate-800 dark:text-slate-200">
                    This DPA forms part of the Terms of Service and governs the processing of personal data by SimHPC.
                </p>
            </div>
        </PageLayout>
    );
}
