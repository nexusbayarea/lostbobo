import { motion } from 'framer-motion';
import { PageLayout } from '@/components/PageLayout';
import { Users, Cpu, Shield, Globe } from 'lucide-react';

export function About() {
    return (
        <PageLayout>
            <div className="pt-32 pb-20 px-6 max-w-6xl mx-auto">
                <h1 className="text-4xl font-bold mb-6 text-slate-900 dark:text-white">About SimHPC</h1>
                <p className="text-lg text-slate-600 dark:text-slate-400">
                    SimHPC bridges the gap between heavy-lift engineering physics and cloud-native agility.
                </p>
            </div>
        </PageLayout>
    );
}
