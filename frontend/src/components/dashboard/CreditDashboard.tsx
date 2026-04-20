import React, { useEffect, useState } from 'react';
import { supabase } from '../../lib/supabase';
import { useAuth } from '../../hooks/useAuth';
import { CreditCard, History, Zap, ArrowUpRight, ArrowDownLeft } from 'lucide-react';

const CreditDashboard = () => {
  const { user } = useAuth();
  const [balance, setBalance] = useState<number | null>(null);
  const [ledger, setLedger] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCreditData = async () => {
      if (!user) return;

      // 1. Fetch current balance from Profile
      const { data: profile } = await supabase
        .from('profiles')
        .select('credit_balance')
        .eq('id', user.id)
        .single();

      // 2. Fetch last 5 transactions from Ledger
      const { data: transactions } = await supabase
        .from('credit_ledger')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })
        .limit(5);

      setBalance(profile?.credit_balance ?? 0);
      setLedger(transactions ?? []);
      setLoading(false);
    };

    fetchCreditData();

    // Real-time subscription to balance changes
    const channel = supabase
      .channel('credit-updates')
      .on('postgres_changes', { event: 'UPDATE', schema: 'public', table: 'profiles', filter: `id=eq.${user?.id}` }, 
      payload => {
        setBalance(payload.new.credit_balance);
      })
      .subscribe();

    return () => { supabase.removeChannel(channel); };
  }, [user]);

  if (loading) return <div className="animate-pulse text-gray-500">Syncing credits...</div>;

  return (
    <div className="space-y-6">
      {/* 1. The Hero: Balance Card */}
      <div className="bg-gradient-to-br from-gray-800 to-gray-900 p-8 rounded-2xl border border-gray-700 shadow-xl relative overflow-hidden">
        <Zap className="absolute -right-4 -top-4 w-32 h-32 text-cyan-500/10 rotate-12" />
        
        <div className="flex justify-between items-start">
          <div>
            <p className="text-gray-400 text-sm font-medium uppercase tracking-wider">Available Compute Credits</p>
            <h2 className="text-5xl font-extrabold text-white mt-2 flex items-center">
              {balance}
              <span className="text-lg text-cyan-400 ml-3 font-normal">Credits</span>
            </h2>
          </div>
          <button className="bg-cyan-600 hover:bg-cyan-500 text-white px-6 py-2 rounded-lg font-bold transition-all flex items-center gap-2 shadow-lg shadow-cyan-900/20">
            <CreditCard size={18} />
            Top Up
          </button>
        </div>
        
        <p className="text-gray-500 text-xs mt-6">
          Standard simulations consume 1 credit per successful run.
        </p>
      </div>

      {/* 2. Recent Activity: The Ledger */}
      <div className="bg-gray-800/50 rounded-2xl border border-gray-700 overflow-hidden">
        <div className="p-5 border-b border-gray-700 flex items-center gap-2">
          <History size={18} className="text-cyan-400" />
          <h3 className="font-bold text-white">Credit Activity</h3>
        </div>
        
        <div className="divide-y divide-gray-800">
          {ledger.length === 0 ? (
            <div className="p-8 text-center text-gray-500 italic">No transaction history found.</div>
          ) : (
            ledger.map((entry) => (
              <div key={entry.id} className="p-4 flex justify-between items-center hover:bg-gray-800 transition-colors">
                <div className="flex items-center gap-4">
                  <div className={`p-2 rounded-full ${entry.amount > 0 ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                    {entry.amount > 0 ? <ArrowUpRight size={16} /> : <ArrowDownLeft size={16} />}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-200 capitalize">
                      {entry.reason.replace(/_/g, ' ')}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(entry.created_at).toLocaleDateString()} at {new Date(entry.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
                <div className={`font-mono font-bold ${entry.amount > 0 ? 'text-green-400' : 'text-gray-300'}`}>
                  {entry.amount > 0 ? `+${entry.amount}` : entry.amount}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default CreditDashboard;
