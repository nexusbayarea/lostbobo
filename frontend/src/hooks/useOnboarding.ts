import { useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { toast } from 'sonner';

export const useOnboarding = (userId: string | undefined) => {
  useEffect(() => {
    const runOnboarding = async () => {
      if (!userId) return;

      // Check if user has already seen the welcome
      const hasSeen = localStorage.getItem(`onboarded_${userId}`);
      if (hasSeen) return;

      const { data, error } = await supabase.rpc('gift_signup_bonus', { 
        target_user_id: userId 
      });

      if (!error) {
        toast.success("Welcome! 10 Credits have been added to your account.", {
          description: "Start your first simulation to see the system in action.",
          duration: 6000,
        });
        localStorage.setItem(`onboarded_${userId}`, 'true');
      }
    };

    runOnboarding();
  }, [userId]);
};
