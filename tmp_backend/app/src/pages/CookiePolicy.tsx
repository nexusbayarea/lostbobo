import { PageLayout } from '@/components/PageLayout';
import { Cookie } from 'lucide-react';

export function CookiePolicy() {
    return (
        <PageLayout>
            <div className="pt-32 pb-20 px-6 max-w-4xl mx-auto">
                <h1 className="text-4xl font-bold mb-6 text-slate-900 dark:text-white">Cookie Policy</h1>
                <p className="text-slate-600 dark:text-slate-400 mb-8">
                    Effective Date: March 3, 2026.
                </p>
                <p className="text-slate-800 dark:text-slate-200">
                    This policy explains how SimHPC uses cookies and similar technologies to recognize you when you visit our website.
                    California residents have the right to opt-out of non-essential tracking.
                </p>
            </div>
        </PageLayout>
    );
}
