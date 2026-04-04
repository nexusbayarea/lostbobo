import { motion } from 'framer-motion';
import { Check } from 'lucide-react';
import { Link } from 'react-router-dom';

const plans = [
  {
    name: 'Free',
    price: '$0',
    desc: 'For learning and exploration',
    features: ['10 simulations/week', 'Shared GPU', 'Basic reports', 'Community support'],
    cta: 'Get Started',
    href: '/signup',
    popular: false,
  },
  {
    name: 'Pro',
    price: '$29',
    desc: 'For professional engineers',
    features: ['Unlimited simulations', 'Dedicated GPU', 'AI reports', 'Priority support', 'API access'],
    cta: 'Start Pro Trial',
    href: '/signup',
    popular: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    desc: 'For teams and organizations',
    features: ['Everything in Pro', 'Team management', 'Custom compute', 'SLA guarantee', 'On-premise option'],
    cta: 'Contact Sales',
    href: '/signup',
    popular: false,
  },
];

export function Pricing() {
  return (
    <section className="py-24 bg-slate-900">
      <div className="max-w-7xl mx-auto px-4">
        <h2 className="text-3xl font-bold text-white text-center mb-12">Pricing</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {plans.map((plan, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              viewport={{ once: true }}
              className={`relative bg-slate-950 border rounded-2xl p-8 ${
                plan.popular ? 'border-cyan-500' : 'border-slate-800'
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-cyan-500 text-white text-xs font-bold rounded-full">
                  Most Popular
                </div>
              )}
              <h3 className="text-xl font-bold text-white mb-1">{plan.name}</h3>
              <div className="text-4xl font-bold text-white mb-1">{plan.price}</div>
              <p className="text-slate-400 text-sm mb-6">{plan.desc}</p>
              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, j) => (
                  <li key={j} className="flex items-center gap-2 text-slate-300 text-sm">
                    <Check className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>
              <Link
                to={plan.href}
                className={`block text-center px-6 py-3 rounded-xl font-medium transition-colors ${
                  plan.popular
                    ? 'bg-cyan-500 hover:bg-cyan-600 text-white'
                    : 'bg-slate-800 hover:bg-slate-700 text-white'
                }`}
              >
                {plan.cta}
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
