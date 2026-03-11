import { PageLayout } from '@/components/PageLayout';
import { ShieldCheck } from 'lucide-react';

export function CCPA() {
    return (
        <PageLayout>
            <div className="pt-32 pb-20 px-6 max-w-4xl mx-auto">
                <h1 className="text-4xl font-bold mb-6 text-slate-900 dark:text-white">CCPA Privacy Notice</h1>
                <p className="text-slate-600 dark:text-slate-400 mb-8">
                    California Consumer Privacy Act Compliance
                </p>
                <p className="text-slate-800 dark:text-slate-200">
                    This Privacy Notice supplements the information contained in our Privacy Policy and applies solely to all visitors, users, and others who reside in the State of California.
                </p>
            </div>
        </PageLayout>
    );
}
